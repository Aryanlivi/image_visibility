const apiUrl = window.location.origin + '/yt_ftp/api/urls/';
const urlList = document.getElementById('url-list');
const addUrlForm = document.getElementById('add-url-form');
const editForm = document.getElementById('edit-url-form');
const modal = new bootstrap.Modal(document.getElementById('editModal'));

// Function to fetch URLs from the backend
async function fetchUrls() {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const urls = await response.json();

        // Clear the URL list
        urlList.innerHTML = '';

        // Create cards for each URL
        urls.forEach((url) => {
            const card = document.createElement('li');
            card.className = 'list-group-item d-flex justify-content-between align-items-center';
            card.style.cursor = 'pointer';

            // Card content
            card.innerHTML = `
                <div>
                    <h5>${url.name}</h5>
                    <p class="mb-1">${url.url}</p>
                </div>
                <span class="badge ${url.active ? 'bg-success' : 'bg-danger'}">
                    ${url.active ? 'Active' : 'Inactive'}
                </span> 
            `;

            // Add click event to the card
            card.addEventListener('click', () => {
                populateEditForm(url);
                modal.show();
            });

            urlList.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching URLs:', error);
    }
}


let initialData = {};
// Function to populate the edit form with data
function populateEditForm(url) {
    initialData = {
        ...url,
        image_metadata:{...url.image_metadata} } // Deep copy of image_metadata
    document.getElementById('edit-url').value = url.url;
    document.getElementById('edit-name').value = url.name;
    document.getElementById('edit-capture-interval').value = url.capture_interval;
    document.getElementById('edit-active').value=url.active;
    document.getElementById('edit-device-id').value = url.image_metadata.device_id;
    document.getElementById('edit-device-code').value = url.image_metadata.devicecode;
    document.getElementById('edit-album-code').value = url.image_metadata.album_code;
    document.getElementById('edit-latitude').value = url.image_metadata.latitude;
    document.getElementById('edit-longitude').value = url.image_metadata.longitude;
    document.getElementById('edit-altitude').value = url.image_metadata.altitude;
    document.getElementById('edit-image-owner').value = url.image_metadata.imageowner;
    document.getElementById('edit-angle').value = url.image_metadata.angle;
    
    //Preserve The id for later delete function
    document.getElementById('editModal').setAttribute('data-id', url.id);
    // Add an event listener for form submission
    editForm.onsubmit = (e) => {
        e.preventDefault();
        updateUrl(url.id);
    };
}

// Function to send the updated data to the backend
async function updateUrl(id) {
    const updatedData = {};
    const currentData = {
        url: document.getElementById('edit-url').value,
        name: document.getElementById('edit-name').value,
        capture_interval: document.getElementById('edit-capture-interval').value,
        active:document.getElementById('edit-active').value,
        image_metadata:{
                device_id: document.getElementById('edit-device-id').value,
                devicecode: document.getElementById('edit-device-code').value,
                album_code: document.getElementById('edit-album-code').value,
                latitude: document.getElementById('edit-latitude').value,
                longitude: document.getElementById('edit-longitude').value,
                altitude: document.getElementById('edit-altitude').value,
                imageowner: document.getElementById('edit-image-owner').value,
                angle: document.getElementById('edit-angle').value
            }
        }
        // Compare each field and add only the changed fields to the updatedData object
        for (const key in currentData) {
            if (key === 'image_metadata') {
                // Compare nested fields in image_metadata
                updatedData.image_metadata = {};
                for (const nestedKey in currentData.image_metadata) {
                    if (currentData.image_metadata[nestedKey] != initialData.image_metadata[nestedKey]) {
                        updatedData.image_metadata[nestedKey] = currentData.image_metadata[nestedKey];
                    }
                }
                // Remove image_metadata if no changes were found in its fields
                if (Object.keys(updatedData.image_metadata).length === 0) {
                    delete updatedData.image_metadata;
                }
            } else {
                // Compare top-level fields
                if (currentData[key] != initialData[key]) {
                    updatedData[key] = currentData[key];
                }
            }
        }

    // If there are no changes, do not send the request
    if (Object.keys(updatedData).length === 0) {
        alert('No changes detected.');
        return;
    }

    try {
        const response = await fetch(`${apiUrl}${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedData),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        alert('URL updated successfully!');
        modal.hide();
        fetchUrls(); // Refresh the list
    } catch (error) {
        console.error('Error updating URL:', error);
        alert("Error updating")
    }
}
// Function to delete a URL
async function deleteUrl(id) {
    const confirmed = confirm("Are you sure you want to delete this URL?");
    if (!confirmed) return;

    try {
        const response = await fetch(`${apiUrl}${id}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        alert('URL deleted successfully!');
        modal.hide();
        fetchUrls(); // Refresh the list
    } catch (error) {
        console.error('Error deleting URL:', error);
        alert("Error deleting");
    }
}
// Event listener for the delete button
document.getElementById('delete-url-btn').addEventListener('click', () => {
    const modal = document.getElementById('editModal');
    const id = modal.getAttribute('data-id'); // Get the ID from the modal's data attribute
    deleteUrl(id);
});
// Call the function to fetch URLs on page load
fetchUrls();

// Function to add a new URL
async function addUrl(event) {
    event.preventDefault(); // Prevent form submission
    const urlInput = document.getElementById('url-input');
    const nameInput = document.getElementById('name');
    const captureIntervalInput = document.getElementById('capture_interval');
    const activeInput=document.getElementById('active');
    const deviceIdInput = document.getElementById('device_id');
    const deviceCodeInput = document.getElementById('devicecode');
    const albumCodeInput = document.getElementById('album_code');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    const altitudeInput = document.getElementById('altitude');
    const imageOwnerInput = document.getElementById('imageowner');
    const angleInput = document.getElementById('angle');
    
    const url = urlInput.value.trim();
    const name = nameInput.value.trim();
    const captureInterval = parseInt(captureIntervalInput.value.trim());
    const active=activeInput.value;
    const deviceId = parseInt(deviceIdInput.value.trim());
    const deviceCode = deviceCodeInput.value.trim();
    const albumCode = albumCodeInput.value.trim();
    const latitude = parseFloat(latitudeInput.value.trim());
    const longitude = parseFloat(longitudeInput.value.trim());
    const altitude = parseFloat(altitudeInput.value.trim());
    const imageOwner = imageOwnerInput.value.trim();
    const angle = parseFloat(angleInput.value.trim());

    // Validate the URL input
    if (!url) {
        alert('Please enter a valid YouTube URL.');
        return;
    }

    // Validate other required fields
    if (!name || !captureInterval || !deviceId || !deviceCode || !albumCode || isNaN(latitude) || isNaN(longitude) || isNaN(altitude) || !imageOwner || isNaN(angle)) {
        alert('Please fill out all fields correctly.');
        return;
    }
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {  
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                name,
                capture_interval: captureInterval,
                active:active,
                image_metadata: {
                    device_id: deviceId,
                    devicecode: deviceCode,
                    album_code: albumCode,
                    latitude: latitude,
                    longitude: longitude,
                    altitude: altitude,
                    imageowner: imageOwner,
                    angle: angle                                 
                }
            }),
        });

        if (!response.ok) throw new Error('Failed to add URL.');
        alert('URL added successfully!');
        urlInput.value = ''; // Clear the input field
        nameInput.value = '';
        captureIntervalInput.value = '';
        deviceIdInput.value = '';
        deviceCodeInput.value = '';
        albumCodeInput.value = '';
        latitudeInput.value = '';
        longitudeInput.value = '';
        altitudeInput.value = '';
        imageOwnerInput.value = '';
        angleInput.value = '';
        fetchUrls(); // Refresh the list
    } catch (error) {
        console.error(error);
        alert('Error adding URL: ' + error.message);
    }
}


document.getElementById("search").addEventListener("input", function () {
    // console.log("Search input detected:", this.value); // Debugging log
    searchURLs();
});


function searchURLs() {
    let query = document.getElementById('search').value.trim();

    if (query === "") {
        fetchUrls(); // Reload full list when search is empty
        return;
    }

    fetch(`${apiUrl}?name__icontains=${encodeURIComponent(query)}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        urlList.innerHTML = ""; // Clear existing results

        if (data.length === 0) {
            let noResult = document.createElement("li");
            noResult.textContent = "No results found";
            noResult.classList.add("list-group-item", "text-muted");
            urlList.appendChild(noResult);
            return;
        }

        data.forEach(url => {
            const card = document.createElement('li');
            card.className = 'list-group-item d-flex justify-content-between align-items-center';
            card.style.cursor = 'pointer';

            card.innerHTML = `
                <div>
                    <h5>${url.name}</h5>
                    <p class="mb-1">${url.url}</p>
                </div>
                <span class="badge ${url.active ? 'bg-success' : 'bg-danger'}">
                    ${url.active ? 'Active' : 'Inactive'}
                </span> 
            `;

            // Add click event for editing
            card.addEventListener('click', () => {
                populateEditForm(url);
                modal.show();
            });

            urlList.appendChild(card);
        });
    })
    .catch(error => {
        console.error("Error fetching search data:", error);
    });
}

// Initialize the app
addUrlForm.addEventListener('submit', addUrl);
fetchUrls(); 
