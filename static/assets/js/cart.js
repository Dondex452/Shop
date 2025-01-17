// Add this at the top of cart.js
function addToCart(productId) {
    fetch(`/add_to_cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart count
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
            
            // Refresh the cart sidebar
            refreshCartSidebar();
            
            // Show success message
            showNotification('Product added to cart successfully!');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to add product to cart', 'error');
    });
}

// Function to refresh cart sidebar
function refreshCartSidebar() {
    fetch('/cart')
        .then(response => response.text())
        .then(html => {
            // Update the cart sidebar content
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const sidebarContent = doc.getElementById('sidebar-cart');
            if (sidebarContent) {
                document.getElementById('sidebar-cart').innerHTML = sidebarContent.innerHTML;
            }
            
            // Reattach event listeners to the new elements
            attachCartEventListeners();
        });
}

// Function to show notifications
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Function to attach event listeners to cart elements
function attachCartEventListeners() {
    // Remove item buttons in sidebar
    document.querySelectorAll('#sidebar-cart .remove-item').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            removeCartItem(productId);
        });
    });

    // Quantity inputs in sidebar
    document.querySelectorAll('#sidebar-cart .quantity input').forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.closest('.product-item').dataset.productId;
            updateCartItem(productId, this.value);
        });
    });
}

// Modified removeCartItem function
function deleteCartItem(productId) {
    fetch(`/remove_from_cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the item from the sidebar
            const item = document.querySelector(`[data-product-id="${productId}"]`);
            if (item) item.remove();
            
            // Update cart count
            updateCartCount(data.cart_count);
            
            // Update totals
            updateCartTotals(data);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateQuantity(productId, change) {
    const quantityInput = document.querySelector(`[data-product-id="${productId}"] .number`);
    let newQuantity = parseInt(quantityInput.value) + change;
    if (newQuantity < 1) newQuantity = 1;
    
    fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            quantityInput.value = newQuantity;
            updateCartTotals(data);
            updateCartCount(data.cart_count);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) cartCount.textContent = count;
}

function updateCartTotals(data) {
    const subtotal = document.getElementById('cartSubtotal');
    const tax = document.getElementById('cartTax');
    const total = document.getElementById('cartTotal');
    
    if (subtotal) subtotal.textContent = `$${data.subtotal.toFixed(2)}`;
    if (tax) tax.textContent = `$${data.tax.toFixed(2)}`;
    if (total) total.textContent = `$${data.grand_total.toFixed(2)}`;
}

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Quantity increment/decrement buttons
    document.querySelectorAll('.increment, .decrement').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.closest('[data-product-id]').dataset.productId;
            const change = this.classList.contains('increment') ? 1 : -1;
            updateQuantity(productId, change);
        });
    });
});

// Add this to your DOMContentLoaded event
document.addEventListener('DOMContentLoaded', function() {
    attachCartEventListeners();
});

// Add this to your layout.html or in a separate JS file
document.addEventListener('DOMContentLoaded', function() {
    // Update quantity
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.closest('tr').dataset.id;
            updateCartItem(productId, this.value);
        });
    });

    // Remove item
    document.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.closest('tr').dataset.id;
            removeCartItem(productId);
        });
    });
});

function updateCartItem(productId, quantity) {
    fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: parseInt(quantity)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart totals
            document.getElementById('itemsTotal').textContent = data.subtotal.toFixed(2);
            document.getElementById('tax').textContent = data.tax.toFixed(2);
            document.getElementById('grandTotal').textContent = data.grand_total.toFixed(2);
            
            // Update cart count in header
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function removeCartItem(productId) {
    fetch(`/remove_from_cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the row from the table
            const row = document.querySelector(`tr[data-id="${productId}"]`);
            if (row) {
                row.remove();
            }
            
            // Update totals
            document.getElementById('itemsTotal').textContent = data.subtotal.toFixed(2);
            document.getElementById('tax').textContent = data.tax.toFixed(2);
            document.getElementById('grandTotal').textContent = data.grand_total.toFixed(2);
            
            // Update cart count in header
            const cartCount = document.querySelector('.cart-count');
            if (cartCount) {
                cartCount.textContent = data.cart_count;
            }
            
            // If cart is empty, show empty message
            if (data.cart_count === 0) {
                const tbody = document.getElementById('cartItems');
                tbody.innerHTML = '<tr><td colspan="6">Your cart is empty.</td></tr>';
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Update the miniCart function in app.js or add to cart.js
document.querySelector(".cart-button").addEventListener("click", function() {
    // Call after popup is opened
    setTimeout(attachCartEventListeners, 100);
});

// Update quantity controls
function initQuantityControls() {
    document.querySelectorAll('.quantity-wrap').forEach(wrap => {
        const input = wrap.querySelector('.number');
        const productId = wrap.closest('[data-product-id]')?.dataset.productId;
        
        wrap.querySelector('.increment').addEventListener('click', function(e) {
            e.preventDefault();
            if (productId) {
                updateQuantity(productId, 1);
            }
        });
        
        wrap.querySelector('.decrement').addEventListener('click', function(e) {
            e.preventDefault();
            if (productId) {
                updateQuantity(productId, -1);
            }
        });
    });
}

// Add this to your DOMContentLoaded listener
document.addEventListener('DOMContentLoaded', function() {
    initQuantityControls();
});

