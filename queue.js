// Function to fetch songs and add them to the grid container
function fetchSongsAndAddToGrid() {
    fetch('user_profiles.json') // Adjust the path if necessary
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const songs = Object.entries(data).map(([user, songData]) => ({
                user,
                song: songData.song,
                bits: songData.priority ? 'High Priority' : 'Regular', // Customize bits display as needed
                type: songData.priority ? 'priority' : 'regular',
            }));
            addSongsToGrid(songs); // Pass the songs to your grid function
        })
        .catch(error => console.error('Error loading the JSON file:', error));
}

// Function to add songs to the grid container
function addSongsToGrid(songs) {
    const gridContainer = document.getElementById("grid_container");

    // Create a wrapper div for the scrolling effect
    const wrapper = document.createElement('div');
    wrapper.style.height = '100%';
    wrapper.style.overflowY = 'hidden'; // Hide overflow
    wrapper.style.position = 'absolute';
    wrapper.style.width = '100%';
    gridContainer.appendChild(wrapper);

    songs.forEach(song => {
        const songElement = document.createElement("div");
        songElement.className = song.type === "priority" ? "priority_cws" : "regular_cws";
        songElement.innerHTML = `
            <input type="checkbox" class="checkbox_done">
            <div id="user_name">${song.user}</div>
            <div id="song_name">${song.song.length > 25 ? song.song.slice(0, 25) + '...' : song.song}</div>
            <div id="bit_amount">${song.bits}</div>
        `;
        wrapper.appendChild(songElement);
    });

    // Start scrolling the wrapper
    let scrollHeight = wrapper.scrollHeight; // Total height of the items
    let currentScroll = 0;

    const scrollSpeed = 1; // Change this for speed

    function scroll() {
        currentScroll += scrollSpeed; // Move scroll position
        if (currentScroll > scrollHeight) {
            currentScroll = 0; // Reset to the start
        }
        wrapper.style.transform = `translateY(-${currentScroll}px)`; // Scroll effect
        requestAnimationFrame(scroll); // Request next frame
    }

    scroll(); // Start scrolling
}

// Call the function to fetch songs and populate the grid
fetchSongsAndAddToGrid();
