// Function to fetch user profiles from a JSON file
async function fetchUserProfiles() {
    try {
        const response = await fetch('user_profiles.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const userProfiles = await response.json();
        createSongList(userProfiles); // Call function to create song list with fetched data
    } catch (error) {
        console.error('Error fetching user profiles:', error);
    }
}

// Function to create song list items
function createSongList(userProfiles) {
    const songQueue = document.getElementById('songQueue');

    // Clear any existing list items
    songQueue.innerHTML = '';

    userProfiles.forEach((profile, index) => {
        const listItem = document.createElement('li');
        listItem.classList.add('song-item');

        // Add priority or source class for background color
        if (profile.priority) {
            listItem.classList.add('priority');
        } else {
            listItem.classList.add(profile.cws_source);
        }

        // Truncate the song title if it exceeds 25 characters
        const songTitle = profile.song.length > 15 ? profile.song.substring(0, 25) + '...' : profile.song;

        // Create a count number element
        const countNumber = document.createElement('span');
        countNumber.textContent = index + 1; // Display the count starting from 1
        countNumber.style.width = '30px'; // Set a fixed width for alignment
        countNumber.style.textAlign = 'left'; // Ensure text is left-aligned
        countNumber.style.display = 'inline-block'; // Keep it inline with checkbox

        // Create the checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.addEventListener('change', () => {
            // Handle the checked state
            if (checkbox.checked) {
                // Add 'checked' class to listItem
                listItem.classList.add('checked');

                // Remove priority class to enforce grey background
                listItem.classList.remove('priority');
            } else {
                // Remove 'checked' class when unchecked
                listItem.classList.remove('checked');

                // Re-add priority class if needed
                if (profile.priority) {
                    listItem.classList.add('priority');
                }
            }
        });

        // Create the content
        const content = `${profile.user_name} - ${songTitle} - $${profile.amount} - ${profile.length_mins} mins`;

        // Append elements to the list item
        listItem.appendChild(countNumber);
        listItem.appendChild(checkbox);
        listItem.appendChild(document.createTextNode(content)); // Append content after the count number and checkbox

        // Append to the song queue
        songQueue.appendChild(listItem);
    });

    // Duplicate the song list for endless scrolling
    const clone = songQueue.cloneNode(true);
    songQueue.parentElement.appendChild(clone); // Append the cloned list
}

// Fetch user profiles and create the song list
fetchUserProfiles();
