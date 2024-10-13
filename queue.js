let autoScrollEnabled = false; // Track if auto-scrolling is enabled
let isPaused = false; // Track if scrolling is paused
let scrollInterval; // Variable to hold the scroll interval

// Check if local storage has data for checkbox states
const checkboxStates = JSON.parse(localStorage.getItem('checkboxStates')) || {};

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

function createSongList(userProfiles) {
    const songQueue = document.getElementById('songQueue');

    // Clear any existing list items
    songQueue.innerHTML = '';

    userProfiles.forEach((profile, index) => {
        const listItem = document.createElement('li');
        listItem.classList.add('song-item');

        // Restore checkbox state from local storage
        if (checkboxStates[`cb${index}`]) {
            listItem.classList.add('checked', 'strikethrough');
            listItem.classList.remove('priority'); // Remove priority class if checked
        } else {
            if (profile.priority) {
                listItem.classList.add('priority'); // Add priority class if applicable
            } else {
                listItem.classList.add(profile.cws_source); // Add source class
            }
        }

        // Create a count number element
        const countNumber = document.createElement('span');
        countNumber.classList.add('count-number');
        countNumber.textContent = index + 1; // Display the count starting from 1

        // Create the custom checkbox wrapper
        const checkboxWrapper = document.createElement('div');
        checkboxWrapper.className = 'checkbox-wrapper-10';

        // Create the checkbox input
        const checkbox = document.createElement('input');
        checkbox.className = 'tgl tgl-flip';
        checkbox.id = `cb${index}`;
        checkbox.type = 'checkbox'; // Checkbox input

        // Set checkbox state based on stored value
        checkbox.checked = checkboxStates[`cb${index}`] || false;

        // Create the label for the checkbox
        const label = document.createElement('label');
        label.className = 'tgl-btn';
        label.setAttribute('data-tg-off', 'on Deck');
        label.setAttribute('data-tg-on', 'Done!');
        label.setAttribute('for', `cb${index}`);

        // Append the checkbox and label to the wrapper
        checkboxWrapper.appendChild(checkbox);
        checkboxWrapper.appendChild(label);

        // Add checkbox event listener for grey-out effect
        checkbox.addEventListener('change', () => {
            // Check if the checkbox is checked
            if (checkbox.checked) {
                listItem.classList.add('checked'); // Greys out row
                listItem.classList.add('strikethrough'); // Add strikethrough effect
                listItem.classList.remove('priority'); // Remove priority class

                // Additionally remove specific source classes
                listItem.classList.remove('dlc');
                listItem.classList.remove('regular');

                // Store the checkbox state in local storage
                checkboxStates[`cb${index}`] = true;
            } else {
                listItem.classList.remove('checked'); // Remove grey
                listItem.classList.remove('strikethrough'); // Remove strikethrough effect

                // Check if it was priority or regular
                if (profile.priority) {
                    listItem.classList.add('priority'); // Re-add priority class
                } else {
                    listItem.classList.add(profile.cws_source); // Re-add source class
                }

                // Store the checkbox state in local storage
                checkboxStates[`cb${index}`] = false;
            }
            localStorage.setItem('checkboxStates', JSON.stringify(checkboxStates)); // Update local storage
        });

        // Create the content with a character limit for song titles
        const trimmedSong = profile.song.length > 15 ? profile.song.substring(0, 15) + '...' : profile.song;
        const content = `@${profile.user_name} - ${trimmedSong} - ${profile.amount} Bits - ${profile.length_mins} mins`;

        listItem.appendChild(countNumber);
        listItem.appendChild(checkboxWrapper); // Append checkbox wrapper
        listItem.appendChild(document.createTextNode(content)); // Append content

        // Append to the song queue
        songQueue.appendChild(listItem);
    });

    // Check the number of users to enable auto-scroll
    if (userProfiles.length >= 7) {
        enableAutoScroll();
    }
}

function enableAutoScroll() {
    if (autoScrollEnabled) return; // Prevent multiple intervals

    autoScrollEnabled = true;

    // Start the auto-scroll interval
    scrollInterval = setInterval(() => {
        if (!isPaused) {
            const songQueue = document.getElementById('songQueue');
            const firstChild = songQueue.firstElementChild;

            if (firstChild) {
                // Move the first child to the bottom of the list
                songQueue.appendChild(firstChild);
            }
        }
    }, 3000); // Adjust the interval duration as needed
}

// Pause auto-scroll on hover
const scrollContainer = document.querySelector('.scroll-container');
scrollContainer.addEventListener('mouseenter', () => {
    isPaused = true; // Set paused state to true
});

scrollContainer.addEventListener('mouseleave', () => {
    isPaused = false; // Reset paused state to false
});

// Fetch user profiles and create the song list
fetchUserProfiles();

