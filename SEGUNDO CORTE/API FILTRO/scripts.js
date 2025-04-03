function handleEnter(event) {
    if(event.key === 'Enter') searchImages();
}

let selectedImages = [];
let currentImages = [];

async function searchImages() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    if(!searchTerm) return;

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ query: searchTerm })
        });
        
        currentImages = await response.json();
        selectedImages = [];
        displayImages(currentImages);
        
    } catch(error) {
        alert(`Error: ${error.message}`);
    }
}

function displayImages(images) {
    const grid = document.getElementById('imageGrid');
    grid.innerHTML = '';
    
    images.forEach(img => {
        const isSelected = selectedImages.some(selected => selected.id === img.id);
        const card = document.createElement('div');
        card.className = 'image-card';
        card.innerHTML = `
            <div class="checkbox-container">
                <input type="checkbox" ${isSelected ? 'checked' : ''} 
                       onchange="toggleSelection(${img.id}, this.checked)">
            </div>
            <img src="${img.webformatURL}" alt="${img.tags}">
        `;
        grid.appendChild(card);
    });
}

function toggleSelection(imageId, isChecked) {
    const image = currentImages.find(img => img.id === imageId);
    if (!image) return;

    if (isChecked) {
        if (!selectedImages.some(img => img.id === imageId)) {
            selectedImages.push(image);
        }
    } else {
        selectedImages = selectedImages.filter(img => img.id !== imageId);
    }
}

async function saveSelected() {
    if (selectedImages.length === 0) {
        alert('Selecciona al menos una imagen');
        return;
    }

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ images: selectedImages })
        });
        
        const result = await response.json();
        if (result.success) {
            alert(`${selectedImages.length} imágenes guardadas exitosamente!`);
            selectedImages = [];
            displayImages(currentImages);
        } else {
            alert('Error al guardar: ' + (result.message || 'Desconocido'));
        }
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}