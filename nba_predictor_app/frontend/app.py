import streamlit as st
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import asyncio
import pandas as pd
import time
import aiohttp
import json

st.set_page_config(
    page_title="NBA Player Predictions (MCP, Streamlit, FastAPI)",
    page_icon="",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stat-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e1e1e;
        margin: 10px;
    }
    .big-number {
        font-size: 24px;
        font-weight: bold;
        color: #00ff00;
    }
    </style>
""", unsafe_allow_html=True)

st.title("NBA Player Predictions (MCP, Streamlit, FastAPI)")
st.markdown("Enter a player's name to view their statistics across different seasons.")

# Initialize MCP client
if 'mcp_client' not in st.session_state:
    with st.spinner("Connecting to MCP server..."):
        try:
            async def init_client():
                st.write("Initializing SSE client...")
                
                # Create a session for health check
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get("http://127.0.0.1:6274/sse") as response:
                            st.write("Server response status:", response.status)
                            headers = dict(response.headers)
                            st.write("Server response headers:", headers)
                            
                            if response.status != 200:
                                raise Exception(f"Server returned status {response.status}")
                            
                            if 'content-type' not in headers or 'text/event-stream' not in headers['content-type'].lower():
                                raise Exception("Server did not return correct content type")
                    except Exception as e:
                        st.error(f"Failed to connect to server: {str(e)}")
                        raise

                try:
                    # Initialize MCP client with proper headers
                    client = sse_client(
                        "http://127.0.0.1:6274/sse",
                        headers={
                            "Accept": "text/event-stream",
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive"
                        }
                    )
                    st.write("Created SSE client")
                    
                    read_stream, write_stream = await client.__aenter__()
                    st.write("Got read/write streams")
                    
                    session = ClientSession(read_stream, write_stream)
                    st.write("Created client session")
                    
                    await session.__aenter__()
                    st.write("Entered client session context")
                    
                    # Initialize with timeout
                    try:
                        await asyncio.wait_for(session.initialize(), timeout=5.0)
                        st.write("Initialized session")
                        return session
                    except asyncio.TimeoutError:
                        st.error("Timeout while initializing session")
                        await session.__aexit__(None, None, None)
                        raise
                    except Exception as e:
                        st.error(f"Error during session initialization: {str(e)}")
                        await session.__aexit__(None, None, None)
                        raise
                except Exception as e:
                    st.error(f"Failed to create MCP client: {str(e)}")
                    raise

            # Run the async initialization
            st.session_state.mcp_client = asyncio.run(init_client())
            st.success("✅ Connected to MCP server successfully!")
        
        except Exception as e:
            st.error(f"❌ Error initializing MCP client: {str(e)}")
            st.info("Check the server logs for more details")
            st.stop()

client = st.session_state.mcp_client

# Test the connection by listing available tools
tools = asyncio.run(client.list_tools())
st.write("Available tools:", tools)

# Create two columns for the input fields
col1, col2 = st.columns(2)

with col1:
    first_name = st.text_input("First Name", placeholder="e.g., Stephen")

with col2:
    last_name = st.text_input("Last Name", placeholder="e.g., Curry")

# Search button
if st.button("Search Player", type="primary"):
    if first_name and last_name:
        with st.spinner("Searching for player..."):
            try:
                # Search for player
                response = client.call_tool(
                    "search_player",
                    first_name=first_name,
                    last_name=last_name
                )

                if response.get("success"):
                    player = response["player"]
                    st.session_state.player = player
                    st.session_state.player_id = player["id"]
                    
                    # Display player info
                    st.subheader(f"📊 {player['first_name']} {player['last_name']}")
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.info(f"Team: {player.get('team', 'N/A')}")
                    with info_cols[1]:
                        st.info(f"Active: {'Yes' if player['is_active'] else 'No'}")
                    with info_cols[2]:
                        st.info(f"Player ID: {player['id']}")

                    # Get available seasons
                    seasons_response = client.call_tool(
                        "get_available_seasons",
                        player_id=player["id"]
                    )

                    if seasons_response.get("success"):
                        st.session_state.available_seasons = seasons_response["seasons"]
                        # Sort seasons in descending order
                        st.session_state.available_seasons.sort(reverse=True)
                else:
                    st.error(f"Player not found: {first_name} {last_name}")
            except Exception as e:
                st.error(f"Error connecting to server: {str(e)}")
    else:
        st.warning("Please enter both first and last name.")

# Season selector and stats display
if "player" in st.session_state and "available_seasons" in st.session_state:
    selected_season = st.selectbox(
        "Select Season",
        st.session_state.available_seasons,
        index=0
    )

    if selected_season:
        with st.spinner("Loading statistics..."):
            try:
                stats_response = client.call_tool(
                    "get_player_stats",
                    player_id=st.session_state.player_id,
                    season=selected_season
                )

                if stats_response.get("success"):
                    stats = stats_response["stats"]
                    
                    # Create three columns for main stats
                    stat_cols = st.columns(5)
                    
                    with stat_cols[0]:
                        st.markdown("""
                            <div class="stat-card">
                                <h3>Points Per Game</h3>
                                <p class="big-number">{:.1f}</p>
                            </div>
                        """.format(stats.get("PTS", 0)), unsafe_allow_html=True)

                    with stat_cols[1]:
                        st.markdown("""
                            <div class="stat-card">
                                <h3>Rebounds Per Game</h3>
                                <p class="big-number">{:.1f}</p>
                            </div>
                        """.format(stats.get("REB", 0)), unsafe_allow_html=True)

                    with stat_cols[2]:
                        st.markdown("""
                            <div class="stat-card">
                                <h3>Assists Per Game</h3>
                                <p class="big-number">{:.1f}</p>
                            </div>
                        """.format(stats.get("AST", 0)), unsafe_allow_html=True)

                    with stat_cols[3]:
                        st.markdown("""
                            <div class="stat-card">
                                <h3>Steals Per Game</h3>
                                <p class="big-number">{:.1f}</p>
                            </div>
                        """.format(stats.get("STL", 0)), unsafe_allow_html=True)

                    with stat_cols[4]:
                        st.markdown("""
                            <div class="stat-card">
                                <h3>Blocks Per Game</h3>
                                <p class="big-number">{:.1f}</p>
                            </div>
                        """.format(stats.get("BLK", 0)), unsafe_allow_html=True)

                    # Additional stats in a table
                    st.subheader("Detailed Statistics")
                    detailed_stats = {
                        "Games Played": stats.get("GP", 0),
                        "Minutes Per Game": stats.get("MIN", 0),
                        "Field Goal %": f"{stats.get('FG_PCT', 0) * 100:.1f}%",
                        "3-Point %": f"{stats.get('FG3_PCT', 0) * 100:.1f}%",
                        "Free Throw %": f"{stats.get('FT_PCT', 0) * 100:.1f}%",
                        "Turnovers": stats.get("TOV", 0),
                    }
                    
                    df = pd.DataFrame([detailed_stats]).T.reset_index()
                    df.columns = ["Statistic", "Value"]
                    st.dataframe(
                        df,
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.error(f"Error loading stats: {stats_response.get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to server: {str(e)}") 