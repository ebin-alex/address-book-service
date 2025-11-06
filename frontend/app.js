const API_BASE_URL = 'http://localhost:8000';

let currentPage = 1;
let currentPageSize = 10;
let currentQuery = '';
let currentTag = '';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadContacts();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('newContactBtn').addEventListener('click', () => openModal());
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('clearBtn').addEventListener('click', clearSearch);
    document.getElementById('contactForm').addEventListener('submit', saveContact);
    document.getElementById('prevBtn').addEventListener('click', () => changePage(-1));
    document.getElementById('nextBtn').addEventListener('click', () => changePage(1));
    document.getElementById('pageSize').addEventListener('change', (e) => {
        currentPageSize = parseInt(e.target.value);
        currentPage = 1;
        loadContacts();
    });
    document.querySelector('.close').addEventListener('click', closeModal);
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('contactModal');
        if (e.target === modal) {
            closeModal();
        }
    });
}

async function loadContacts() {
    try {
        let url = `${API_BASE_URL}/contacts?page=${currentPage}&page_size=${currentPageSize}`;
        const response = await fetch(url);
        const data = await response.json();
        displayContacts(data);
    } catch (error) {
        showError('Failed to load contacts: ' + error.message);
    }
}

async function performSearch() {
    currentQuery = document.getElementById('searchInput').value.trim();
    currentTag = document.getElementById('tagFilter').value.trim();
    currentPage = 1;
    
    try {
        let url = `${API_BASE_URL}/contacts/search?page=${currentPage}&page_size=${currentPageSize}`;
        if (currentQuery) url += `&query=${encodeURIComponent(currentQuery)}`;
        if (currentTag) url += `&tag=${encodeURIComponent(currentTag)}`;
        
        const response = await fetch(url);
        const data = await response.json();
        displayContacts(data);
    } catch (error) {
        showError('Search failed: ' + error.message);
    }
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('tagFilter').value = '';
    currentQuery = '';
    currentTag = '';
    currentPage = 1;
    loadContacts();
}

function displayContacts(data) {
    const contactsList = document.getElementById('contactsList');
    const pageInfo = document.getElementById('pageInfo');
    
    pageInfo.textContent = `Page ${data.page} of ${data.total_pages} (${data.total} total)`;
    
    document.getElementById('prevBtn').disabled = data.page <= 1;
    document.getElementById('nextBtn').disabled = data.page >= data.total_pages;
    
    if (data.contacts.length === 0) {
        contactsList.innerHTML = '<div class="empty-state"><h3>No contacts found</h3><p>Click "New Contact" to add one!</p></div>';
        return;
    }
    
    contactsList.innerHTML = data.contacts.map(contact => `
        <div class="contact-card">
            <div class="contact-name">${escapeHtml(contact.name)}</div>
            ${contact.email ? `<div class="contact-info">📧 ${escapeHtml(contact.email)}</div>` : ''}
            ${contact.phone ? `<div class="contact-info">📞 ${escapeHtml(contact.phone)}</div>` : ''}
            ${contact.phone_numbers && contact.phone_numbers.length > 0 
                ? contact.phone_numbers.map(pn => `<div class="contact-info">📞 ${escapeHtml(pn.number)}</div>`).join('')
                : ''}
            ${contact.addresses && contact.addresses.length > 0 
                ? contact.addresses.map(addr => `<div class="contact-info">📍 ${escapeHtml(addr.address)}</div>`).join('')
                : ''}
            ${contact.tags && contact.tags.length > 0 
                ? `<div class="contact-tags">${contact.tags.map(tag => `<span class="tag">${escapeHtml(tag.name)}</span>`).join('')}</div>`
                : ''}
            <div class="contact-actions">
                <button class="btn btn-edit btn-small" onclick="editContact(${contact.id})">Edit</button>
                <button class="btn btn-danger btn-small" onclick="deleteContact(${contact.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function openModal(contactId = null) {
    const modal = document.getElementById('contactModal');
    const form = document.getElementById('contactForm');
    const modalTitle = document.getElementById('modalTitle');
    
    form.reset();
    document.getElementById('contactId').value = '';
    document.getElementById('phoneNumbersList').innerHTML = '';
    document.getElementById('addressesList').innerHTML = '';
    
    if (contactId) {
        modalTitle.textContent = 'Edit Contact';
        loadContactForEdit(contactId);
    } else {
        modalTitle.textContent = 'New Contact';
    }
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('contactModal').style.display = 'none';
}

async function loadContactForEdit(contactId) {
    try {
        const response = await fetch(`${API_BASE_URL}/contacts/${contactId}`);
        const contact = await response.json();
        
        document.getElementById('contactId').value = contact.id;
        document.getElementById('name').value = contact.name;
        document.getElementById('email').value = contact.email || '';
        document.getElementById('phone').value = contact.phone || '';
        document.getElementById('tags').value = contact.tags ? contact.tags.map(t => t.name).join(', ') : '';
        
        // Load phone numbers
        contact.phone_numbers.forEach(pn => {
            addPhoneNumberField(pn.number);
        });
        
        // Load addresses
        contact.addresses.forEach(addr => {
            addAddressField(addr.address);
        });
    } catch (error) {
        showError('Failed to load contact: ' + error.message);
    }
}

function addPhoneNumber(number = '') {
    addPhoneNumberField(number);
}

function addPhoneNumberField(number = '') {
    const container = document.getElementById('phoneNumbersList');
    const div = document.createElement('div');
    div.className = 'phone-number-item';
    div.innerHTML = `
        <input type="text" class="phone-number-input" value="${escapeHtml(number)}" placeholder="Phone number">
        <button type="button" class="btn btn-danger btn-small" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(div);
}

function addAddress(address = '') {
    addAddressField(address);
}

function addAddressField(address = '') {
    const container = document.getElementById('addressesList');
    const div = document.createElement('div');
    div.className = 'address-item';
    div.innerHTML = `
        <input type="text" class="address-input" value="${escapeHtml(address)}" placeholder="Address">
        <button type="button" class="btn btn-danger btn-small" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(div);
}

async function saveContact(e) {
    e.preventDefault();
    hideError();
    
    const contactId = document.getElementById('contactId').value;
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const tags = document.getElementById('tags').value.split(',').map(t => t.trim()).filter(t => t);
    
    // Collect phone numbers
    const phoneNumbers = Array.from(document.querySelectorAll('.phone-number-input'))
        .map(input => input.value.trim())
        .filter(val => val)
        .map(val => ({ number: val }));
    
    // Collect addresses
    const addresses = Array.from(document.querySelectorAll('.address-input'))
        .map(input => input.value.trim())
        .filter(val => val)
        .map(val => ({ address: val }));
    
    const contactData = {
        name,
        email: email || null,
        phone: phone || null,
        phone_numbers: phoneNumbers,
        addresses: addresses,
        tags: tags
    };
    
    try {
        let url = `${API_BASE_URL}/contacts`;
        let method = 'POST';
        
        if (contactId) {
            url += `/${contactId}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(contactData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save contact');
        }
        
        closeModal();
        loadContacts();
    } catch (error) {
        showError('Failed to save contact: ' + error.message);
    }
}

async function editContact(contactId) {
    openModal(contactId);
}

async function deleteContact(contactId) {
    if (!confirm('Are you sure you want to delete this contact?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/contacts/${contactId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete contact');
        }
        
        loadContacts();
    } catch (error) {
        showError('Failed to delete contact: ' + error.message);
    }
}

function changePage(delta) {
    currentPage += delta;
    if (currentQuery || currentTag) {
        performSearch();
    } else {
        loadContacts();
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    setTimeout(() => hideError(), 5000);
}

function hideError() {
    document.getElementById('errorMessage').classList.remove('show');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

