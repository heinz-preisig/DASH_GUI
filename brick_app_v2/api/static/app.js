// Brick App v2 Web Interface JavaScript

let currentBrick = null;
let libraries = [];
let bricks = [];

// Initialize the application
async function init() {
    await loadLibraries();
    await loadBricks();
    setupEventListeners();
}

// Load libraries
async function loadLibraries() {
    try {
        const response = await fetch('/api/libraries');
        const data = await response.json();
        libraries = data.data.libraries || [];
        
        console.log('Loaded libraries:', libraries);
        
        const select = document.getElementById('librarySelect');
        select.innerHTML = '<option value="">All Libraries</option>';
        libraries.forEach(lib => {
            const option = document.createElement('option');
            option.value = lib.name;
            option.textContent = lib.name;
            select.appendChild(option);
            console.log(`Added library option: "${lib.name}" with value "${lib.name}"`);
        });
    } catch (error) {
        showMessage('Error loading libraries: ' + error.message, 'error');
    }
}

// Load bricks
async function loadBricks() {
    try {
        const response = await fetch('/api/bricks');
        const data = await response.json();
        bricks = data.data.bricks || [];
        
        console.log('Loaded bricks:', bricks);
        bricks.forEach((brick, index) => {
            console.log(`Brick ${index}:`, brick.name);
            console.log(`  Constraints:`, brick.constraints);
            console.log(`  Properties:`, brick.properties);
        });
        
        displayBricks(bricks);
    } catch (error) {
        showMessage('Error loading bricks: ' + error.message, 'error');
    }
}

// Display bricks in the sidebar
function displayBricks(brickList) {
    const brickListElement = document.getElementById('brickList');
    brickListElement.innerHTML = '';
    
    brickList.forEach(brick => {
        const li = document.createElement('li');
        li.className = 'brick-item';
        li.onclick = () => selectBrick(brick);
        li.innerHTML = `
            <div class="brick-name">${brick.name}</div>
            <div class="brick-description">${brick.description}</div>
        `;
        brickListElement.appendChild(li);
    });
}

// Select a brick
function selectBrick(brick) {
    console.log('Selecting brick:', brick);
    currentBrick = brick;
    
    // Update selection in list
    document.querySelectorAll('.brick-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.target.closest('.brick-item').classList.add('selected');
    
    // Display brick details
    displayBrickDetails(brick);
    displayProperties(brick);
    displayConstraints(brick);
    
    updateStatus(`Selected: ${brick.name}`);
}

// Display brick details
function displayBrickDetails(brick) {
    const detailsElement = document.getElementById('brickDetails');
    detailsElement.innerHTML = `
        <div class="form-group">
            <label>Name</label>
            <input type="text" id="brickName" value="${brick.name}">
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea id="brickDescription">${brick.description}</textarea>
        </div>
        <div class="form-group">
            <label>Type</label>
            <select id="brickType">
                <option value="NodeShape" ${brick.object_type === 'NodeShape' ? 'selected' : ''}>NodeShape</option>
                <option value="PropertyShape" ${brick.object_type === 'PropertyShape' ? 'selected' : ''}>PropertyShape</option>
            </select>
        </div>
        <div class="form-group">
            <label>Target Class</label>
            <input type="text" id="brickTarget" value="${brick.target_class || ''}">
        </div>
    `;
}

// Display properties
function displayProperties(brick) {
    const propertiesElement = document.getElementById('propertiesSection');
    const properties = brick.properties || {};
    
    if (Object.keys(properties).length === 0) {
        propertiesElement.innerHTML = '<p>No properties defined.</p>';
        return;
    }
    
    let html = '<ul class="properties-list">';
    for (const [path, property] of Object.entries(properties)) {
        // Handle SHACL property structure
        const propPath = typeof property === 'object' ? property.path : path;
        const propDatatype = typeof property === 'object' ? property.datatype : 'xsd:string';
        const propDefaultValue = typeof property === 'object' ? property.defaultValue : '';
        const propDescription = typeof property === 'object' ? property.description : '';
        
        const propConstraints = typeof property === 'object' ? property.constraints || [] : [];
        
        // Build constraint details display
        let constraintDetails = '';
        if (propConstraints.length > 0) {
            constraintDetails = '<br><div style="margin-top: 0.5rem;">';
            propConstraints.forEach((constraint, index) => {
                const constraintType = constraint.constraint_type || constraint.type || 'Unknown';
                const constraintValue = constraint.value || 'No value';
                const constraintDescription = (constraint.parameters && constraint.parameters.description) || (constraint.description) || '';
                constraintDetails += `
                    <div style="background: #f8f9fa; padding: 0.25rem 0.5rem; margin: 0.25rem 0; border-radius: 3px; font-size: 0.8rem;">
                        <span style="color: #e67e22; font-weight: 600;">${constraintType}:</span> ${constraintValue}
                        ${constraintDescription ? `<br><small style="color: #95a5a6;">${constraintDescription}</small>` : ''}
                        <button class="btn btn-secondary" onclick="editPropertyConstraint('${path}', ${index})" style="padding: 0.1rem 0.3rem; font-size: 0.7rem; margin-left: 0.5rem;">Edit</button>
                        <button class="btn btn-secondary" onclick="deletePropertyConstraint('${path}', ${index})" style="padding: 0.1rem 0.3rem; font-size: 0.7rem; margin-left: 0.25rem;">×</button>
                    </div>
                `;
            });
            constraintDetails += '</div>';
        }
        
        html += `
            <li class="property-item">
                <div>
                    <strong>${propPath}</strong>
                    <span style="color: #7f8c8d; font-size: 0.8rem;"> (${propDatatype})</span>
                    ${propDefaultValue ? `<br><small style="color: #3498db;">Default: ${propDefaultValue}</small>` : ''}
                    ${propDescription ? `<br><small style="color: #95a5a6;">${propDescription}</small>` : ''}
                    ${propConstraints.length > 0 ? `<br><small style="color: #e67e22;">${propConstraints.length} constraint(s)</small>` : ''}
                    ${constraintDetails}
                </div>
                <div>
                    <button class="btn btn-secondary" onclick="editProperty('${path}')" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Edit</button>
                    <button class="btn btn-secondary" onclick="addPropertyConstraint('${path}')" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.25rem;">+C</button>
                    <button class="btn btn-secondary" onclick="deleteProperty('${path}')" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.25rem;">Delete</button>
                </div>
            </li>
        `;
    }
    html += '</ul>';
    
    propertiesElement.innerHTML = html;
}

// Display constraints
function displayConstraints(brick) {
    const constraintsElement = document.getElementById('constraintsSection');
    const constraints = brick.constraints || [];
    
    console.log('Displaying constraints for brick:', brick.name);
    console.log('Constraints array:', constraints);
    console.log('Constraints length:', constraints.length);
    
    if (constraints.length === 0) {
        constraintsElement.innerHTML = '<p>No constraints defined.</p>';
        return;
    }
    
    let html = '<ul class="constraint-list">';
    constraints.forEach((constraint, index) => {
        console.log(`Constraint ${index}:`, constraint);
        console.log('Constraint keys:', Object.keys(constraint));
        
        // Handle different constraint structures
        const constraintType = constraint.constraint_type || constraint.type || 'Unknown';
        const constraintValue = constraint.value || 'No value';
        const constraintDescription = (constraint.parameters && constraint.parameters.description) || (constraint.description) || '';
        
        console.log(`Parsed constraint: type=${constraintType}, value=${constraintValue}`);
        
        html += `
            <li class="constraint-item">
                <div>
                    <strong>${constraintType}:</strong> ${constraintValue}
                    ${constraintDescription ? `<br><small style="color: #95a5a6;">${constraintDescription}</small>` : ''}
                </div>
                <div>
                    <button class="btn btn-secondary" onclick="editConstraint(${index})" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Edit</button>
                    <button class="btn btn-secondary" onclick="deleteConstraint(${index})" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.25rem;">Delete</button>
                </div>
            </li>
        `;
    });
    html += '</ul>';
    
    console.log('Generated HTML:', html);
    constraintsElement.innerHTML = html;
}

// Create new brick
function createNewBrick() {
    currentBrick = {
        brick_id: 'new_' + Date.now(),
        name: 'New Brick',
        description: '',
        object_type: 'NodeShape',
        target_class: '',
        properties: {},
        constraints: [],
        library: 'default'
    };
    
    displayBrickDetails(currentBrick);
    displayProperties(currentBrick);
    displayConstraints(currentBrick);
    
    // Clear selection
    document.querySelectorAll('.brick-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    updateStatus('Creating new brick');
}

// Save current brick
async function saveCurrentBrick() {
    if (!currentBrick) {
        showMessage('No brick selected', 'error');
        return;
    }
    
    // Update brick data from form
    currentBrick.name = document.getElementById('brickName').value;
    currentBrick.description = document.getElementById('brickDescription').value;
    currentBrick.object_type = document.getElementById('brickType').value;
    currentBrick.target_class = document.getElementById('brickTarget').value;
    
    try {
        // First create a session if we don't have one
        let sessionResponse = await fetch('/api/session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_type: 'web',
                user_info: {}
            })
        });
        
        if (!sessionResponse.ok) {
            throw new Error('Failed to create session');
        }
        
        const sessionData = await sessionResponse.json();
        const sessionId = sessionData.data.session_id;
        
        // Save the brick using the session-based API
        const saveResponse = await fetch(`/api/session/${sessionId}/brick/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                brick_data: currentBrick
            })
        });
        
        if (saveResponse.ok) {
            showMessage('Brick saved successfully', 'success');
            await loadBricks(); // Reload bricks
            updateStatus(`Saved: ${currentBrick.name}`);
        } else {
            const errorData = await saveResponse.json();
            showMessage('Error saving brick: ' + (errorData.message || saveResponse.statusText), 'error');
        }
    } catch (error) {
        showMessage('Error saving brick: ' + error.message, 'error');
    }
}

// Delete current brick
function deleteCurrentBrick() {
    if (!currentBrick) {
        showMessage('No brick selected', 'error');
        return;
    }
    
    if (confirm(`Are you sure you want to delete "${currentBrick.name}"?`)) {
        showMessage('Delete functionality not yet implemented', 'error');
        updateStatus('Delete not implemented');
    }
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('librarySelect').addEventListener('change', filterBricks);
    document.getElementById('brickTypeSelect').addEventListener('change', filterBricks);
}

// Filter bricks based on library and type
function filterBricks() {
    const selectedLibrary = document.getElementById('librarySelect').value;
    const selectedType = document.getElementById('brickTypeSelect').value;
    
    let filteredBricks = bricks;
    
    // Filter by library
    if (selectedLibrary) {
        filteredBricks = filteredBricks.filter(brick => brick.library === selectedLibrary);
    }
    
    // Filter by type
    if (selectedType) {
        filteredBricks = filteredBricks.filter(brick => brick.object_type === selectedType);
    }
    
    displayBricks(filteredBricks);
    
    // Update status
    const libText = selectedLibrary ? `Library: ${selectedLibrary}` : 'All Libraries';
    const typeText = selectedType ? `Type: ${selectedType}` : 'All Types';
    updateStatus(`Filtered: ${libText}, ${typeText} (${filteredBricks.length} bricks)`);
}

// Show message
function showMessage(message, type = 'info') {
    const messagesElement = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = type;
    messageDiv.textContent = message;
    messagesElement.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Update status
function updateStatus(text) {
    document.getElementById('statusText').textContent = text;
}

// Property management functions
function addProperty() {
    if (!currentBrick) {
        showMessage('No brick selected', 'error');
        return;
    }
    
    showPropertyEditor();
}

// Show property editor dialog
function showPropertyEditor(propertyKey = '', propertyValue = '', propertyType = 'xsd:string', propertyDescription = '') {
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3 class="modal-header">${propertyKey ? 'Edit Property' : 'Add Property'}</h3>
            
            <div class="form-group">
                <label for="propPath">Property Path</label>
                <div style="display: flex; gap: 0.5rem;">
                    <input type="text" id="propPath" value="${propertyKey}" placeholder="e.g., foaf:name, schema:email, age" 
                           style="flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                    <button class="btn btn-secondary" onclick="showPropertyPathBrowser()" style="padding: 0.5rem;">Browse</button>
                </div>
            </div>
            
            <div class="form-group">
                <label for="propDatatype">Datatype</label>
                <div style="display: flex; gap: 0.5rem;">
                    <select id="propDatatype" style="flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                        <option value="xsd:string" ${propertyType === 'xsd:string' ? 'selected' : ''}>xsd:string</option>
                        <option value="xsd:integer" ${propertyType === 'xsd:integer' ? 'selected' : ''}>xsd:integer</option>
                        <option value="xsd:decimal" ${propertyType === 'xsd:decimal' ? 'selected' : ''}>xsd:decimal</option>
                        <option value="xsd:boolean" ${propertyType === 'xsd:boolean' ? 'selected' : ''}>xsd:boolean</option>
                        <option value="xsd:date" ${propertyType === 'xsd:date' ? 'selected' : ''}>xsd:date</option>
                        <option value="xsd:dateTime" ${propertyType === 'xsd:dateTime' ? 'selected' : ''}>xsd:dateTime</option>
                        <option value="xsd:anyURI" ${propertyType === 'xsd:anyURI' ? 'selected' : ''}>xsd:anyURI</option>
                        <option value="xsd:float" ${propertyType === 'xsd:float' ? 'selected' : ''}>xsd:float</option>
                        <option value="xsd:double" ${propertyType === 'xsd:double' ? 'selected' : ''}>xsd:double</option>
                        <option value="xsd:duration" ${propertyType === 'xsd:duration' ? 'selected' : ''}>xsd:duration</option>
                    </select>
                    <button class="btn btn-secondary" onclick="showDatatypeBrowser()" style="padding: 0.5rem;">Info</button>
                </div>
            </div>
            
            <div class="form-group">
                <label for="propValue">Default Value (optional)</label>
                <input type="text" id="propValue" value="${propertyValue}" placeholder="Enter default value (optional)" 
                       style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <div class="form-group">
                <label for="propDescription">Description (optional)</label>
                <textarea id="propDescription" placeholder="Describe this property" 
                          style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; height: 60px; resize: vertical;">${propertyDescription}</textarea>
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="saveProperty('${propertyKey}')">Save Property</button>
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Focus on the path input
    setTimeout(() => {
        document.getElementById('propPath').focus();
    }, 100);
}

// Save property from editor
function saveProperty(originalKey = '') {
    const path = document.getElementById('propPath').value.trim();
    const datatype = document.getElementById('propDatatype').value;
    const defaultValue = document.getElementById('propValue').value.trim();
    const description = document.getElementById('propDescription').value.trim();
    
    if (!path) {
        showMessage('Property path is required', 'error');
        return;
    }
    
    // Validate path format
    if (!path.match(/^[a-zA-Z][a-zA-Z0-9_:-]*$/)) {
        showMessage('Property path must be a valid identifier (e.g., foaf:name, schema:email)', 'error');
        return;
    }
    
    if (!currentBrick.properties) {
        currentBrick.properties = {};
    }
    
    // Remove old property if editing
    if (originalKey && originalKey !== path) {
        delete currentBrick.properties[originalKey];
    }
    
    // Store property with SHACL structure
    currentBrick.properties[path] = {
        path: path,
        datatype: datatype,
        description: description,
        created_at: new Date().toISOString()
    };
    
    // Add default value if provided
    if (defaultValue) {
        // Validate default value based on datatype
        if (datatype === 'xsd:integer' && !/^-?\d+$/.test(defaultValue)) {
            showMessage('Default value must be an integer', 'error');
            return;
        }
        
        if (datatype === 'xsd:decimal' && !/^-?\d*\.?\d+$/.test(defaultValue)) {
            showMessage('Default value must be a decimal number', 'error');
            return;
        }
        
        if (datatype === 'xsd:boolean' && !['true', 'false'].includes(defaultValue.toLowerCase())) {
            showMessage('Default value must be true or false', 'error');
            return;
        }
        
        if (datatype === 'xsd:anyURI' && !defaultValue.match(/^https?:\/\/|^\w+:/)) {
            showMessage('Default value must be a valid URI', 'error');
            return;
        }
        
        currentBrick.properties[path].defaultValue = defaultValue;
    }
    
    displayProperties(currentBrick);
    document.querySelector('.modal').remove();
    
    const action = originalKey ? 'updated' : 'added';
    showMessage(`Property ${action}: ${path}`, 'success');
    updateStatus(`${action.charAt(0).toUpperCase() + action.slice(1)} property: ${path}`);
}

// Edit property
function editProperty(propertyPath) {
    if (!currentBrick || !currentBrick.properties[propertyPath]) {
        showMessage('Property not found', 'error');
        return;
    }
    
    const property = currentBrick.properties[propertyPath];
    const propPath = typeof property === 'object' ? property.path : propertyPath;
    const propDatatype = typeof property === 'object' ? property.datatype : 'xsd:string';
    const propDefaultValue = typeof property === 'object' ? property.defaultValue : '';
    const propDescription = typeof property === 'object' ? property.description : '';
    
    showPropertyEditor(propPath, propDefaultValue, propDatatype, propDescription);
}

// Delete property
function deleteProperty(propertyKey) {
    if (!currentBrick || !currentBrick.properties[propertyKey]) {
        showMessage('Property not found', 'error');
        return;
    }
    
    if (confirm(`Are you sure you want to delete property "${propertyKey}"?`)) {
        delete currentBrick.properties[propertyKey];
        displayProperties(currentBrick);
        showMessage(`Property deleted: ${propertyKey}`, 'success');
        updateStatus(`Deleted property: ${propertyKey}`);
    }
}

// Show property browser
function showPropertyBrowser() {
    if (!currentBrick) {
        showMessage('No brick selected', 'error');
        return;
    }
    
    // Filter property bricks
    const propertyBricks = bricks.filter(brick => brick.object_type === 'PropertyShape');
    
    let html = '<div class="modal-content"><h3 class="modal-header">Available Property Bricks</h3>';
    html += '<div class="browser-grid">';
    
    propertyBricks.forEach(brick => {
        html += `
            <div class="browser-item" onclick="addPropertyBrick('${brick.brick_id}')">
                <strong>${brick.name}</strong><br>
                <small>${brick.description}</small>
            </div>
        `;
    });
    
    html += '</div>';
    html += '<div class="modal-footer"><button class="btn btn-secondary" onclick="this.closest(\'.modal\').remove()">Close</button></div></div>';
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

// Add property brick to current brick
function addPropertyBrick(propertyBrickId) {
    const propertyBrick = bricks.find(b => b.brick_id === propertyBrickId);
    if (!propertyBrick) return;
    
    if (!currentBrick.properties) {
        currentBrick.properties = {};
    }
    
    // Use the property brick's path as the property key
    const propertyKey = propertyBrick.properties.path || propertyBrick.brick_id;
    currentBrick.properties[propertyKey] = propertyBrick.properties.datatype || 'string';
    
    displayProperties(currentBrick);
    // Remove the property browser modal (the current modal)
    event.target.closest('.modal').remove();
    showMessage(`Added property: ${propertyBrick.name}`, 'success');
    updateStatus(`Added property brick: ${propertyBrick.name}`);
}

// Browser functions
function showPropertyPathBrowser() {
    const commonProperties = [
        { prefix: 'foaf', uri: 'http://xmlns.com/foaf/0.1/', properties: ['name', 'mbox', 'homepage', 'knows', 'member'] },
        { prefix: 'schema', uri: 'http://schema.org/', properties: ['name', 'email', 'url', 'description', 'image', 'birthDate'] },
        { prefix: 'dc', uri: 'http://purl.org/dc/elements/1.1/', properties: ['title', 'creator', 'date', 'description', 'identifier'] },
        { prefix: 'rdfs', uri: 'http://www.w3.org/2000/01/rdf-schema#', properties: ['label', 'comment', 'seeAlso'] },
        { prefix: 'owl', uri: 'http://www.w3.org/2002/07/owl#', properties: ['sameAs', 'differentFrom', 'equivalentClass'] }
    ];
    
    let html = '<div class="modal-content"><h3 class="modal-header">Property Path Browser</h3>';
    html += '<input type="text" placeholder="Search properties..." style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem;" onkeyup="filterProperties(this.value)">';
    
    commonProperties.forEach(onto => {
        html += `
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: #3498db; margin-bottom: 0.5rem;">${onto.prefix} (${onto.uri})</h4>
                <div class="browser-grid">
        `;
        
        onto.properties.forEach(prop => {
            const fullPath = `${onto.prefix}:${prop}`;
            html += `
                <div class="browser-item" onclick="selectPropertyPath('${fullPath}')">
                    <strong>${prop}</strong><br>
                    <small>${fullPath}</small>
                </div>
            `;
        });
        
        html += '</div></div>';
    });
    
    html += `
        <div style="margin-top: 1.5rem;">
            <h4 style="color: #3498db; margin-bottom: 0.5rem;">Custom Property</h4>
            <div style="display: flex; gap: 0.5rem;">
                <input type="text" id="customPrefix" placeholder="prefix" style="flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                <input type="text" id="customProperty" placeholder="property" style="flex: 2; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                <button class="btn btn-primary" onclick="selectCustomProperty()">Add</button>
            </div>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" onclick="this.closest(\'.modal\').remove()">Cancel</button></div>
    `;
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function selectPropertyPath(path) {
    document.getElementById('propPath').value = path;
    // Remove the property browser modal (the current modal)
    event.target.closest('.modal').remove();
    showMessage(`Selected property path: ${path}`, 'success');
}

function selectCustomProperty() {
    const prefix = document.getElementById('customPrefix').value.trim();
    const property = document.getElementById('customProperty').value.trim();
    
    if (!prefix || !property) {
        showMessage('Both prefix and property are required', 'error');
        return;
    }
    
    const fullPath = `${prefix}:${property}`;
    selectPropertyPath(fullPath);
}

function filterProperties(searchTerm) {
    const items = document.querySelectorAll('.browser-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function showDatatypeBrowser() {
    const datatypes = [
        { type: 'xsd:string', description: 'Text strings', example: '"Hello World"' },
        { type: 'xsd:integer', description: 'Whole numbers', example: '42' },
        { type: 'xsd:decimal', description: 'Decimal numbers', example: '3.14' },
        { type: 'xsd:float', description: '32-bit floating point', example: '3.14159' },
        { type: 'xsd:double', description: '64-bit floating point', example: '3.14159265359' },
        { type: 'xsd:boolean', description: 'True/false values', example: 'true' },
        { type: 'xsd:date', description: 'Date (YYYY-MM-DD)', example: '2023-12-25' },
        { type: 'xsd:dateTime', description: 'Date and time', example: '2023-12-25T10:30:00' },
        { type: 'xsd:time', description: 'Time (HH:MM:SS)', example: '10:30:00' },
        { type: 'xsd:duration', description: 'Time duration', example: 'P1Y2M3DT4H5M6S' },
        { type: 'xsd:anyURI', description: 'URI/IRI values', example: 'http://example.com' },
        { type: 'xsd:base64Binary', description: 'Base64 encoded binary', example: 'SGVsbG8gV29ybGQ=' }
    ];
    
    let html = '<div class="modal-content"><h3 class="modal-header">XSD Datatype Reference</h3>';
    html += '<input type="text" placeholder="Search datatypes..." style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem;" onkeyup="filterDatatypes(this.value)">';
    html += '<div style="display: grid; gap: 0.5rem;">';
    
    datatypes.forEach(dt => {
        html += `
            <div class="browser-item" onclick="selectDatatype('${dt.type}')">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${dt.type}</strong>
                        <p style="margin: 0.25rem 0; color: #7f8c8d; font-size: 0.9rem;">${dt.description}</p>
                        <code style="background: #f8f9fa; padding: 0.25rem; border-radius: 3px; font-size: 0.8rem;">Example: ${dt.example}</code>
                    </div>
                    <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Select</button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    html += '<div class="modal-footer"><button class="btn btn-secondary" onclick="this.closest(\'.modal\').remove()">Close</button></div></div>';
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function selectDatatype(datatype) {
    document.getElementById('propDatatype').value = datatype;
    // Remove the datatype browser modal (the current modal)
    event.target.closest('.modal').remove();
    showMessage(`Selected datatype: ${datatype}`, 'success');
}

function filterDatatypes(searchTerm) {
    const items = document.querySelectorAll('.browser-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Constraint management functions
function addConstraint() {
    if (!currentBrick) {
        showMessage('No brick selected', 'error');
        return;
    }
    
    showConstraintEditor();
}

// Show constraint editor dialog
function showConstraintEditor(constraintIndex = -1) {
    const isEdit = constraintIndex >= 0;
    const constraint = isEdit ? currentBrick.constraints[constraintIndex] : null;
    
    console.log('Constraint editor - constraintIndex:', constraintIndex, 'constraint:', constraint);
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    // Get constraint values safely
    const constraintType = constraint?.constraint_type || constraint?.type || '';
    const constraintValue = constraint?.value || '';
    const constraintDescription = constraint?.description || '';
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3 class="modal-header">${isEdit ? 'Edit Constraint' : 'Add Constraint'}</h3>
            
            <div class="form-group">
                <label for="constraintType">Constraint Type</label>
                <div style="display: flex; gap: 0.5rem;">
                    <select id="constraintType" style="flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                        <option value="minCount" ${constraintType === 'minCount' ? 'selected' : ''}>minCount</option>
                        <option value="maxCount" ${constraintType === 'maxCount' ? 'selected' : ''}>maxCount</option>
                        <option value="minLength" ${constraintType === 'minLength' ? 'selected' : ''}>minLength</option>
                        <option value="maxLength" ${constraintType === 'maxLength' ? 'selected' : ''}>maxLength</option>
                        <option value="pattern" ${constraintType === 'pattern' ? 'selected' : ''}>pattern</option>
                        <option value="datatype" ${constraintType === 'datatype' ? 'selected' : ''}>datatype</option>
                        <option value="class" ${constraintType === 'class' ? 'selected' : ''}>class</option>
                        <option value="nodeKind" ${constraintType === 'nodeKind' ? 'selected' : ''}>nodeKind</option>
                        <option value="in" ${constraintType === 'in' ? 'selected' : ''}>in</option>
                        <option value="not" ${constraintType === 'not' ? 'selected' : ''}>not</option>
                        <option value="equals" ${constraintType === 'equals' ? 'selected' : ''}>equals</option>
                        <option value="disjoint" ${constraintType === 'disjoint' ? 'selected' : ''}>disjoint</option>
                        <option value="lessThan" ${constraintType === 'lessThan' ? 'selected' : ''}>lessThan</option>
                        <option value="lessThanOrEquals" ${constraintType === 'lessThanOrEquals' ? 'selected' : ''}>lessThanOrEquals</option>
                    </select>
                    <button class="btn btn-secondary" onclick="showConstraintTypeBrowser()" style="padding: 0.5rem;">Info</button>
                </div>
            </div>
            
            <div class="form-group">
                <label for="constraintValue">Constraint Value</label>
                <input type="text" id="constraintValue" value="${constraintValue}" 
                       placeholder="Enter constraint value" 
                       style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <div class="form-group">
                <label for="constraintDescription">Description (optional)</label>
                <textarea id="constraintDescription" placeholder="Describe this constraint" 
                          style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; height: 60px; resize: vertical;">${constraintDescription}</textarea>
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="saveConstraint(${constraintIndex})">Save Constraint</button>
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Focus on the constraint type input
    setTimeout(() => {
        document.getElementById('constraintType').focus();
    }, 100);
}

// Save constraint from editor
function saveConstraint(constraintIndex) {
    const type = document.getElementById('constraintType').value;
    const value = document.getElementById('constraintValue').value.trim();
    const description = document.getElementById('constraintDescription').value.trim();
    
    if (!type) {
        showMessage('Constraint type is required', 'error');
        return;
    }
    
    if (!value) {
        showMessage('Constraint value is required', 'error');
        return;
    }
    
    // Validate constraint value based on type
    if (['minCount', 'maxCount', 'minLength', 'maxLength'].includes(type) && !/^\d+$/.test(value)) {
        showMessage('Value must be a number for this constraint type', 'error');
        return;
    }
    
    if (type === 'pattern' && !isValidRegex(value)) {
        showMessage('Value must be a valid regular expression', 'error');
        return;
    }
    
    if (!currentBrick.constraints) {
        currentBrick.constraints = [];
    }
    
    // Create constraint data structure compatible with SHACLConstraint
    const constraintData = {
        constraint_type: type,
        value: value,
        parameters: {
            description: description,
            created_at: new Date().toISOString()
        }
    };
    
    if (constraintIndex >= 0) {
        // Update existing constraint
        currentBrick.constraints[constraintIndex] = constraintData;
        showMessage('Constraint updated', 'success');
        updateStatus('Updated constraint');
    } else {
        // Add new constraint
        currentBrick.constraints.push(constraintData);
        showMessage('Constraint added', 'success');
        updateStatus('Added constraint');
    }
    
    displayConstraints(currentBrick);
    document.querySelector('.modal').remove();
}

// Edit constraint
function editConstraint(constraintIndex) {
    if (!currentBrick || !currentBrick.constraints[constraintIndex]) {
        showMessage('Constraint not found', 'error');
        return;
    }
    
    console.log('Editing constraint at index:', constraintIndex);
    showConstraintEditor(constraintIndex);
}

// Delete constraint
function deleteConstraint(constraintIndex) {
    if (!currentBrick || !currentBrick.constraints[constraintIndex]) {
        showMessage('Constraint not found', 'error');
        return;
    }
    
    const constraint = currentBrick.constraints[constraintIndex];
    const constraintType = constraint.constraint_type || constraint.type || 'Unknown';
    const constraintValue = constraint.value || 'No value';
    
    if (confirm(`Are you sure you want to delete constraint "${constraintType}: ${constraintValue}"?`)) {
        currentBrick.constraints.splice(constraintIndex, 1);
        displayConstraints(currentBrick);
        showMessage(`Constraint deleted: ${constraintType}`, 'success');
        updateStatus(`Deleted constraint: ${constraintType}`);
    }
}

// Show constraint browser
function showConstraintBrowser(propertyPath = null) {
    if (!currentBrick) {
        showMessage('No brick selected', 'error');
        return;
    }
    
    const contextualConstraints = getContextualConstraints(propertyPath);
    const recommendations = getRecommendedConstraints(propertyPath);
    
    let html = '<div class="modal-content"><h3 class="modal-header">SHACL Constraint Types</h3>';
    
    if (propertyPath) {
        const property = currentBrick.properties[propertyPath];
        const datatype = property.datatype || 'xsd:string';
        html += `<p style="color: #7f8c8d; margin-bottom: 1rem;">Property: <strong>${propertyPath}</strong> (Type: ${datatype})</p>`;
    }
    
    html += '<input type="text" placeholder="Search constraint types..." style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1rem;" onkeyup="filterConstraintTypes(this.value)">';
    
    // Show recommendations if available
    if (recommendations.length > 0) {
        html += '<div style="margin-bottom: 1.5rem;"><h4 style="color: #3498db; margin-bottom: 0.5rem;">🔥 Recommended for this property</h4>';
        recommendations.forEach(rec => {
            const constraint = contextualConstraints.find(c => c.type === rec.type);
            if (constraint) {
                const priorityColor = rec.priority === 'high' ? '#e74c3c' : rec.priority === 'medium' ? '#f39c12' : '#95a5a6';
                html += `
                    <div class="browser-item" onclick="selectConstraintType('${constraint.type}')" style="border-left: 4px solid ${priorityColor};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${constraint.type}</strong> <span style="color: ${priorityColor}; font-size: 0.8rem;">[${rec.priority.toUpperCase()}]</span>
                                <p style="margin: 0.25rem 0; color: #7f8c8d; font-size: 0.9rem;">${constraint.description}</p>
                                <p style="margin: 0.25rem 0; color: #3498db; font-size: 0.8rem; font-style: italic;">${rec.reason}</p>
                                <code style="background: #f8f9fa; padding: 0.25rem; border-radius: 3px; font-size: 0.8rem;">Example: ${rec.example || constraint.example}</code>
                            </div>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Select</button>
                        </div>
                    </div>
                `;
            }
        });
        html += '</div>';
    }
    
    // Show all applicable constraints
    html += '<div style="margin-bottom: 1.5rem;"><h4 style="color: #3498db; margin-bottom: 0.5rem;">Available Constraints</h4>';
    html += '<div style="display: grid; gap: 0.5rem;">';
    
    contextualConstraints.forEach(ct => {
        const isRecommended = recommendations.some(rec => rec.type === ct.type);
        if (!isRecommended) {
            html += `
                <div class="browser-item" onclick="selectConstraintType('${ct.type}')">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${ct.type}</strong>
                            <p style="margin: 0.25rem 0; color: #7f8c8d; font-size: 0.9rem;">${ct.description}</p>
                            <code style="background: #f8f9fa; padding: 0.25rem; border-radius: 3px; font-size: 0.8rem;">Example: ${ct.example}</code>
                        </div>
                        <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Select</button>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    html += '<div class="modal-footer"><button class="btn btn-secondary" onclick="this.closest(\'.modal\').remove()">Close</button></div></div>';
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

// Show constraint type browser
function showConstraintTypeBrowser() {
    showConstraintBrowser();
}

// Get context-aware constraint recommendations
function getContextualConstraints(propertyPath = null) {
    const constraints = [
        { type: 'minCount', description: 'Minimum number of values', example: '1', applicable: 'all' },
        { type: 'maxCount', description: 'Maximum number of values', example: '5', applicable: 'all' },
        { type: 'minLength', description: 'Minimum string length', example: '3', applicable: 'string' },
        { type: 'maxLength', description: 'Maximum string length', example: '50', applicable: 'string' },
        { type: 'pattern', description: 'Regular expression pattern', example: '^[A-Za-z]+$', applicable: 'string' },
        { type: 'datatype', description: 'Required datatype', example: 'xsd:string', applicable: 'all' },
        { type: 'class', description: 'Required class', example: 'foaf:Person', applicable: 'all' },
        { type: 'nodeKind', description: 'Node kind (blank, iri, literal)', example: 'iri', applicable: 'all' },
        { type: 'in', description: 'List of allowed values', example: '["red", "green", "blue"]', applicable: 'all' },
        { type: 'not', description: 'Negated constraint', example: 'foaf:name', applicable: 'all' },
        { type: 'equals', description: 'Equals another property', example: 'ex:otherProperty', applicable: 'all' },
        { type: 'disjoint', description: 'Disjoint with another property', example: 'ex:otherProperty', applicable: 'all' },
        { type: 'lessThan', description: 'Less than another property', example: 'ex:otherProperty', applicable: 'numeric' },
        { type: 'lessThanOrEquals', description: 'Less than or equal to another property', example: 'ex:otherProperty', applicable: 'numeric' }
    ];
    
    if (!propertyPath || !currentBrick || !currentBrick.properties[propertyPath]) {
        return constraints;
    }
    
    const property = currentBrick.properties[propertyPath];
    const datatype = property.datatype || 'xsd:string';
    
    // Filter constraints based on datatype
    return constraints.filter(constraint => {
        switch (constraint.applicable) {
            case 'string':
                return datatype.includes('string') || datatype.includes('String');
            case 'numeric':
                return datatype.includes('int') || datatype.includes('decimal') || datatype.includes('float') || datatype.includes('double');
            case 'all':
            default:
                return true;
        }
    });
}

// Get recommended constraints for property
function getRecommendedConstraints(propertyPath) {
    if (!propertyPath || !currentBrick || !currentBrick.properties[propertyPath]) {
        return [];
    }
    
    const property = currentBrick.properties[propertyPath];
    const datatype = property.datatype || 'xsd:string';
    const recommendations = [];
    
    // Datatype-specific recommendations
    if (datatype.includes('string')) {
        recommendations.push({
            type: 'minLength',
            reason: 'String properties often need minimum length validation',
            priority: 'medium'
        });
        recommendations.push({
            type: 'maxLength',
            reason: 'String properties often need maximum length validation',
            priority: 'medium'
        });
    }
    
    if (datatype.includes('int') || datatype.includes('decimal') || datatype.includes('float')) {
        recommendations.push({
            type: 'lessThan',
            reason: 'Numeric properties often need range validation',
            priority: 'low'
        });
    }
    
    if (datatype.includes('uri') || datatype.includes('URI')) {
        recommendations.push({
            type: 'pattern',
            reason: 'URI properties often need format validation',
            priority: 'high',
            example: '^https?://.+'
        });
    }
    
    // General recommendations
    recommendations.push({
        type: 'minCount',
        reason: 'Consider if this property is required',
        priority: 'high'
    });
    
    recommendations.push({
        type: 'maxCount',
        reason: 'Consider if this property should be single-valued',
        priority: 'high'
    });
    
    return recommendations;
}

// Select constraint type from browser
function selectConstraintType(constraintType) {
    document.getElementById('constraintType').value = constraintType;
    event.target.closest('.modal').remove();
    showMessage(`Selected constraint type: ${constraintType}`, 'success');
}

// Filter constraint types in browser
function filterConstraintTypes(searchTerm) {
    const items = document.querySelectorAll('.browser-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Property constraint management
function addPropertyConstraint(propertyPath) {
    if (!currentBrick || !currentBrick.properties[propertyPath]) {
        showMessage('Property not found', 'error');
        return;
    }
    
    showPropertyConstraintEditor(propertyPath);
}

// Show property constraint editor dialog
function showPropertyConstraintEditor(propertyPath, constraintIndex = -1) {
    const isEdit = constraintIndex >= 0;
    const property = currentBrick.properties[propertyPath];
    const constraints = property.constraints || [];
    const constraint = isEdit ? constraints[constraintIndex] : null;
    
    const contextualConstraints = getContextualConstraints(propertyPath);
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    let constraintOptions = '';
    contextualConstraints.forEach(ct => {
        const selected = constraint?.constraint_type === ct.type ? 'selected' : '';
        constraintOptions += `<option value="${ct.type}" ${selected}>${ct.type}</option>`;
    });
    
    modal.innerHTML = `
        <div class="modal-content">
            <h3 class="modal-header">${isEdit ? 'Edit Property Constraint' : 'Add Property Constraint'}</h3>
            <p style="color: #7f8c8d; margin-bottom: 1rem;">Property: <strong>${propertyPath}</strong> (Type: ${property.datatype || 'xsd:string'})</p>
            
            <div class="form-group">
                <label for="propertyConstraintType">Constraint Type</label>
                <div style="display: flex; gap: 0.5rem;">
                    <select id="propertyConstraintType" style="flex: 1; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                        ${constraintOptions}
                    </select>
                    <button class="btn btn-secondary" onclick="showConstraintBrowser('${propertyPath}')" style="padding: 0.5rem;">Browse</button>
                </div>
            </div>
            
            <div class="form-group">
                <label for="propertyConstraintValue">Constraint Value</label>
                <input type="text" id="propertyConstraintValue" value="${constraint?.value || ''}" 
                       placeholder="Enter constraint value" 
                       style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <div class="form-group">
                <label for="propertyConstraintDescription">Description (optional)</label>
                <textarea id="propertyConstraintDescription" placeholder="Describe this constraint" 
                          style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; height: 60px; resize: vertical;">${constraint?.description || ''}</textarea>
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="savePropertyConstraint('${propertyPath}', ${constraintIndex})">Save Constraint</button>
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Focus on the constraint type input
    setTimeout(() => {
        document.getElementById('propertyConstraintType').focus();
    }, 100);
}

// Save property constraint from editor
function savePropertyConstraint(propertyPath, constraintIndex) {
    const type = document.getElementById('propertyConstraintType').value;
    const value = document.getElementById('propertyConstraintValue').value.trim();
    const description = document.getElementById('propertyConstraintDescription').value.trim();
    
    if (!type) {
        showMessage('Constraint type is required', 'error');
        return;
    }
    
    if (!value) {
        showMessage('Constraint value is required', 'error');
        return;
    }
    
    // Validate constraint value based on type
    if (['minCount', 'maxCount', 'minLength', 'maxLength'].includes(type) && !/^\d+$/.test(value)) {
        showMessage('Value must be a number for this constraint type', 'error');
        return;
    }
    
    if (type === 'pattern' && !isValidRegex(value)) {
        showMessage('Value must be a valid regular expression', 'error');
        return;
    }
    
    const property = currentBrick.properties[propertyPath];
    if (!property.constraints) {
        property.constraints = [];
    }
    
    // Create constraint data structure compatible with SHACLConstraint
    const constraintData = {
        constraint_type: type,
        value: value,
        parameters: {
            description: description,
            created_at: new Date().toISOString()
        }
    };
    
    if (constraintIndex >= 0) {
        // Update existing constraint
        property.constraints[constraintIndex] = constraintData;
        showMessage('Property constraint updated', 'success');
        updateStatus('Updated property constraint');
    } else {
        // Add new constraint
        property.constraints.push(constraintData);
        showMessage('Property constraint added', 'success');
        updateStatus('Added property constraint');
    }
    
    displayProperties(currentBrick);
    document.querySelector('.modal').remove();
}

// Show property constraints
function showPropertyConstraints(propertyPath) {
    if (!currentBrick || !currentBrick.properties[propertyPath]) {
        showMessage('Property not found', 'error');
        return;
    }
    
    const property = currentBrick.properties[propertyPath];
    const constraints = property.constraints || [];
    
    if (constraints.length === 0) {
        showMessage('No constraints defined for this property', 'info');
        return;
    }
    
    let html = '<div class="modal-content"><h3 class="modal-header">Property Constraints</h3>';
    html += `<p style="color: #7f8c8d; margin-bottom: 1rem;">Property: <strong>${propertyPath}</strong></p>`;
    html += '<div style="display: grid; gap: 0.5rem;">';
    
    constraints.forEach((constraint, index) => {
        html += `
            <div style="padding: 1rem; border: 1px solid #ddd; border-radius: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong>${constraint.constraint_type}:</strong> ${constraint.value}
                        ${constraint.description ? `<br><small style="color: #95a5a6;">${constraint.description}</small>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-secondary" onclick="editPropertyConstraint('${propertyPath}', ${index})" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Edit</button>
                        <button class="btn btn-secondary" onclick="deletePropertyConstraint('${propertyPath}', ${index})" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.25rem;">Delete</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    html += '<div class="modal-footer"><button class="btn btn-secondary" onclick="this.closest(\'.modal\').remove()">Close</button></div></div>';
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

// Edit property constraint
function editPropertyConstraint(propertyPath, constraintIndex) {
    if (!currentBrick || !currentBrick.properties[propertyPath]) {
        showMessage('Property not found', 'error');
        return;
    }
    
    const constraints = currentBrick.properties[propertyPath].constraints || [];
    if (!constraints[constraintIndex]) {
        showMessage('Constraint not found', 'error');
        return;
    }
    
    showPropertyConstraintEditor(propertyPath, constraintIndex);
}

// Delete property constraint
function deletePropertyConstraint(propertyPath, constraintIndex) {
    if (!currentBrick || !currentBrick.properties[propertyPath]) {
        showMessage('Property not found', 'error');
        return;
    }
    
    const constraints = currentBrick.properties[propertyPath].constraints || [];
    if (!constraints[constraintIndex]) {
        showMessage('Constraint not found', 'error');
        return;
    }
    
    const constraint = constraints[constraintIndex];
    if (confirm(`Are you sure you want to delete constraint "${constraint.constraint_type}: ${constraint.value}" from property "${propertyPath}"?`)) {
        constraints.splice(constraintIndex, 1);
        displayProperties(currentBrick);
        showMessage(`Property constraint deleted: ${constraint.constraint_type}`, 'success');
        updateStatus(`Deleted property constraint: ${constraint.constraint_type}`);
    }
}

// Validate regular expression
function isValidRegex(pattern) {
    try {
        new RegExp(pattern);
        return true;
    } catch (e) {
        return false;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', init);
