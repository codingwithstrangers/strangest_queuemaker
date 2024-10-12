// Fetch the song data from the JSON file
fetch('all_songs.json')
    .then(response => response.json())
    .then(data => {
        const songList = document.getElementById('songList');

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

            // Truncate artist and song titles to a maximum of 10 characters
            const artist = song.artist.length > 15 ? song.artist.substring(0, 15) + '...' : song.artist;
            const songTitle = song.song.length > 15 ? song.song.substring(0, 15) + '...' : song.song;

            // Create and append cells
            row.innerHTML = `
                <td>${key}</td>
                <td>- ${artist} - </td>
                <td>${songTitle}</td>
            `;
            songList.appendChild(row);
        }
    })
    .catch(error => console.error('Error fetching song data:', error));
