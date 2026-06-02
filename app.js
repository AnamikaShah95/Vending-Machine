const API_BASE = "http://127.0.0.1:5000/api";

// System State Registries
let cashBalance = 0;
let codeBuffer = "";
let shoppingCart = [];
let loadedCatalog = [];

const itemsGrid = document.getElementById('items-grid');
const screenDisplay = document.getElementById('screen-display');
const cartDisplay = document.getElementById('cart-display');
const coinReturn = document.getElementById('coin-return');
const upiModal = document.getElementById('upi-modal');
const qrContainer = document.getElementById('qrcode-container');
const vendedModal = document.getElementById('vended-modal');
const modalVendedList = document.getElementById('modal-vended-list');

/**
 * REST API Engine Synchronizer
 */
async function syncVendingMachine() {
    try {
        const res = await fetch(`${API_BASE}/products`);
        if (!res.ok) throw new Error("API Route down");
        const data = await res.json();
        
        loadedCatalog = data.products;
        renderGrid(data.products);
    } catch (err) {
        if (screenDisplay) screenDisplay.innerText = "CONN ERROR";
    }
}

/**
 * Telemetry Monitor Polling Routine
 */
async function pollHardwareTelemetry() {
    try {
        const res = await fetch(`${API_BASE}/telemetry`);
        if (!res.ok) throw new Error();
        const data = await res.json();
        
        const tempEl = document.getElementById('telemetry-temp');
        const statusEl = document.getElementById('telemetry-status');
        
        if (tempEl) tempEl.innerText = data.temperature;
        if (statusEl) {
            statusEl.innerText = data.status;
            statusEl.className = "text-emerald-400 font-bold animate-pulse";
        }
    } catch {
        const statusEl = document.getElementById('telemetry-status');
        if (statusEl) {
            statusEl.innerText = "OFFLINE";
            statusEl.className = "text-red-500 font-bold";
        }
    }
}

function renderGrid(productList) {
    if (!itemsGrid || !productList || productList.length === 0) return;
    itemsGrid.innerHTML = "";
    
    productList.forEach(item => {
        const outOfStock = item.quantity <= 0;
        const isSelected = codeBuffer === item.id.toUpperCase();
        
        itemsGrid.innerHTML += `
            <div class="p-3 rounded-2xl border transition-all duration-300 flex flex-col items-center justify-between text-center relative shadow-lg ${isSelected ? 'border-cyan-400 bg-slate-800/60 scale-[1.01]' : 'border-slate-800/60 bg-slate-900/40'} ${outOfStock ? 'opacity-20 pointer-events-none' : ''}">
                <div class="w-20 h-24 flex items-center justify-center mb-1 filter drop-shadow-md ${item.bg_glow}">
                    <img src="${item.image}" alt="${item.name}" class="max-w-full max-h-full object-contain pointer-events-none" />
                </div>
                <span class="text-[11px] font-extrabold text-slate-200 tracking-wide capitalize truncate w-full">${item.name}</span>
                <span class="text-xs font-black text-emerald-400 mt-0.5">Rs. ${item.price}</span>
                
                <div class="w-full bg-black/60 rounded-full h-1 my-2 overflow-hidden border border-zinc-900">
                    <div class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-300" style="width: ${item.quantity * 10}%"></div>
                </div>
                
                <div class="flex justify-between w-full items-center text-[9px] font-semibold px-0.5 text-slate-400 font-mono">
                    <span class="bg-slate-950/80 px-1.5 py-0.5 rounded-md text-slate-500 border border-slate-900">QTY: ${item.quantity}</span>
                    <span class="bg-neutral-950 text-amber-400 font-bold px-2 py-0.5 rounded-md border border-zinc-800 tracking-wider">${item.id}</span>
                </div>
            </div>
        `;
    });
}

function handleDragStart(e, value) {
    e.dataTransfer.setData("text/plain", value);
}

function handleCoinDrop(e) {
    e.preventDefault();
    const tokenValue = parseInt(e.dataTransfer.getData("text/plain"), 10);
    if (tokenValue) {
        cashBalance += tokenValue;
        if (coinReturn) coinReturn.innerText = "";
        refreshDisplay();
    }
}

function pressKey(character) {
    if (!loadedCatalog || loadedCatalog.length === 0) return;

    if (codeBuffer.length < 2) {
        codeBuffer += character.toUpperCase();
        refreshDisplay();
        
        if (codeBuffer.length === 2) {
            const item = loadedCatalog.find(p => p.id.toUpperCase() === codeBuffer);
            
            if (item) {
                const currentInCart = shoppingCart.filter(id => id.toUpperCase() === codeBuffer).length;
                
                if (item.quantity - currentInCart > 0) {
                    shoppingCart.push(codeBuffer);
                    codeBuffer = "";
                    refreshDisplay();
                } else {
                    flashErrorAlert("OUT OF STOCK");
                }
            } else {
                flashErrorAlert("INVALID CODE");
            }
        }
        renderGrid(loadedCatalog);
    }
}

function clearBuffer() {
    codeBuffer = "";
    shoppingCart = [];
    refreshDisplay();
    renderGrid(loadedCatalog);
}

function refreshDisplay() {
    let cashString = cashBalance > 0 ? `Rs. ${cashBalance}` : "INSERT COIN";
    let codeString = codeBuffer.length > 0 ? ` [${codeBuffer}]` : "";
    if (screenDisplay) screenDisplay.innerText = cashString + codeString;
    if (cartDisplay) cartDisplay.innerText = shoppingCart.length > 0 ? `Cart: ${shoppingCart.join(", ")}` : "Cart: Empty";
}

function getCartTotalCost() {
    return shoppingCart.reduce((sum, id) => {
        const match = loadedCatalog.find(p => p.id.toUpperCase() === id.toUpperCase());
        return sum + (match ? match.price : 0);
    }, 0);
}

async function purchaseItem() {
    if (shoppingCart.length === 0) {
        flashErrorAlert("CART EMPTY");
        return;
    }
    const cartTotal = getCartTotalCost();

    if (cashBalance === 0) {
        const priceEl = document.getElementById('upi-cart-price');
        if (priceEl) priceEl.innerText = `Total Order Cost: Rs. ${cartTotal}`;
        if (qrContainer) qrContainer.innerHTML = "";
        
        try {
            if (typeof QRCode !== 'undefined' && qrContainer) {
                new QRCode(qrContainer, {
                    text: `upi://pay?pa=refreshmentnode@bank&pn=RetroVending&am=${cartTotal}&cu=INR`,
                    width: 140,
                    height: 140
                });
                if (upiModal) upiModal.classList.remove('opacity-0', 'pointer-events-none');
            } else {
                simulateUPISettlement();
            }
        } catch(e) {
            simulateUPISettlement();
        }
        return;
    }
    executeCheckoutRequest("cash");
}

async function simulateUPISettlement() {
    if (upiModal) upiModal.classList.add('opacity-0', 'pointer-events-none');
    if (screenDisplay) screenDisplay.innerText = "UPI SUCCESS";
    setTimeout(() => executeCheckoutRequest("upi"), 800);
}

async function executeCheckoutRequest(paymentMode) {
    if (screenDisplay) screenDisplay.innerText = "PROCESSING...";
    try {
        const response = await fetch(`${API_BASE}/order/cart`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cartItems: shoppingCart,
                transactionType: paymentMode,
                insertedAmount: cashBalance
            })
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
            flashErrorAlert(data.message ? data.message.toUpperCase() : "FAILED");
            return;
        }

        // Pass both vended items AND change amount to our pop-up generator
        openVendedModal(data.vended, data.change);
        
        cashBalance = 0; // Reset local balance since change is vended via pop-up
        shoppingCart = [];
        refreshDisplay();
        loadLiveAnalytics();
    } catch (e) {
        flashErrorAlert("SERVER ERR");
    }
}

// FIXED: Added changeAmount parameter to display remaining cash directly in the modal pop-up
function openVendedModal(vendedItemsList, changeAmount = 0) {
    if (!modalVendedList || !vendedModal) return;
    modalVendedList.innerHTML = "";
    
    // 1. Render all the drinks purchased
    vendedItemsList.forEach(item => {
        modalVendedList.innerHTML += `
            <div class="flex flex-col items-center bg-black/40 p-2 rounded-xl border border-zinc-900 w-24">
                <img src="${item.image}" class="w-12 h-14 object-contain" />
                <span class="text-[10px] text-slate-300 font-bold truncate w-full mt-1 capitalize">${item.name}</span>
            </div>
        `;
    });

    // 2. If there is extra money left over, dynamically append a clear change collector card!
    if (changeAmount > 0) {
        modalVendedList.innerHTML += `
            <div class="flex flex-col items-center justify-center bg-amber-500/10 p-2 rounded-xl border border-amber-500/40 w-24 animate-bounce">
                <span class="text-xl">🪙</span>
                <span class="text-[10px] text-amber-400 font-black tracking-wide mt-1">CHANGE</span>
                <span class="text-[11px] text-white font-mono font-bold">Rs. ${changeAmount}</span>
            </div>
        `;
    }

    vendedModal.classList.remove('opacity-0', 'pointer-events-none');
}

function closeVendedModal() {
    if (vendedModal) vendedModal.classList.add('opacity-0', 'pointer-events-none');
    if (screenDisplay) screenDisplay.innerText = "THANK YOU";
    setTimeout(() => { refreshDisplay(); syncVendingMachine(); }, 1200);
}

function returnChange() {
    if (cashBalance > 0) {
        if (coinReturn) coinReturn.innerText = `Rs. ${cashBalance} 🪙`;
        cashBalance = 0;
        refreshDisplay();
    }
}

async function loadLiveAnalytics() {
    try {
        const res = await fetch(`${API_BASE}/admin/analytics`);
        const data = await res.json();
        const revEl = document.getElementById('stat-revenue');
        const txEl = document.getElementById('stat-tx');
        const topEl = document.getElementById('stat-top');
        
        if (revEl) revEl.innerText = data.gross_revenue;
        if (txEl) txEl.innerText = `${data.total_transactions} tx`;
        if (topEl) topEl.innerText = data.top_selling_product;
    } catch (e) {}
}

function flashErrorAlert(msg) {
    if (screenDisplay) screenDisplay.innerText = msg;
    setTimeout(() => { refreshDisplay(); syncVendingMachine(); }, 2000);
}

async function triggerRestock() {
    await fetch(`${API_BASE}/admin/restock`, { method: "POST" });
    syncVendingMachine();
}

window.addEventListener('DOMContentLoaded', async () => {
    await syncVendingMachine();
    await loadLiveAnalytics();
    
    pollHardwareTelemetry();
    setInterval(pollHardwareTelemetry, 4000);
});