const songList = document.getElementById('songList');

// Variable to control scroll state
let isScrolling = true;

// Fetch the song data from the JSON file
fetch('all_songs.json')
    .then(response => response.json())
    .then(data => {
        const rows = [];

        // Loop through the songs and create rows
        for (const key in data) {
            const song = data[key];
            const row = document.createElement('tr');

            // Set the class based on song type
            if (song.type === 'dlc') {
                row.classList.add('tr-dlc');
            } else {
                row.classList.add('tr-regular');
            }

            // Truncate artist and song titles to a maximum of 15 characters
            const artist = song.artist.length > 15 ? song.artist.substring(0, 15) + '...' : song.artist;
            const songTitle = song.song.length > 15 ? song.song.substring(0, 15) + '...' : song.song;

            // Create and append cells
            row.innerHTML = `
                <td>${key}</td>
                <td>- ${artist} - </td>
                <td>${songTitle}</td>
            `;
            rows.push(row);
            songList.appendChild(row);
        }

        // Clone the rows for a seamless scroll effect
        const cloneRows = () => {
            rows.forEach(row => {
                const clone = row.cloneNode(true); // Clone each row
                songList.appendChild(clone); // Append clone to the song list
            });
        };

        // Call the clone function to duplicate the rows
        cloneRows();

        // Create the automatic scrolling functionality
        let scrollSpeed = 1; // Adjust the speed of the scroll
        const scrollList = () => {
            if (isScrolling) {
                songList.scrollTop += scrollSpeed; // Scroll down by scrollSpeed amount

                // When the user scrolls past both the original and duplicated rows, reset to the top
                if (songList.scrollTop >= songList.scrollHeight / 2) {
                    songList.scrollTop = 0; // Reset scroll position to the top
                }
            }
        };

        // Set an interval to scroll the list automatically
        const scrollInterval = setInterval(scrollList, 50);

        // Pause scrolling on hover
        songList.addEventListener('mouseover', () => {
            isScrolling = false; // Stop scrolling when hovering
        });

        // Resume scrolling when not hovering
        songList.addEventListener('mouseout', () => {
            isScrolling = true; // Resume scrolling when not hovering
        });
    })
    .catch(error => console.error('Error fetching song data:', error));
