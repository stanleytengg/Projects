var lastPrices = {};
document.addEventListener('DOMContentLoaded', async () => {
    const symbols = await getAllSymbols();
    var tickers = Array.isArray(symbols) ? symbols : [];
    var counter = 60;

    function startUpdateCycle() {
        updatePrices(); 
        setInterval(() => {
            counter--;
            document.getElementById('counter').textContent = counter;
            if (counter <= 0) {
                updatePrices();
                counter = 60;
            }
        }, 1000)
    }
    
    tickers.forEach(function(ticker) {
        addTickerToGrid(ticker);
    });
    updatePrices();

    document.getElementById('add-ticker-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const tickersInput = document.getElementById('new-ticker').value;
        let tickersArray = tickersInput.split(',').map(ticker => ticker.trim().toUpperCase());
        tickersArray = tickersArray.filter(ticker => ticker != '' && ticker != ' ');
        document.getElementById('new-ticker').value = '';

        for (const ticker of tickersArray) {
            const response = await fetch('/add_ticker', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({'add-ticker': ticker})
            });
    
            const newTicker = await response.json()

            if (newTicker.status != 'error' && response.ok) {
                addTickerToGrid(newTicker.symbol);
                tickers.push(newTicker.symbol);
            }
            else
                alert(newTicker.message);
        }
        
        updatePrices();
    });

    document.getElementById('tickers-table').addEventListener('click', async (e) => {
        if (e.target && e.target.classList.contains('remove-btn')) {
            const tickerToRemove = e.target.getAttribute('data-ticker');
            const response = await fetch(`/remove_ticker/${tickerToRemove}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });
            
            if (response.ok) {
                tickers = tickers.filter(t => t !== tickerToRemove);
                document.getElementById(tickerToRemove).remove();
            }
        }
    });

    document.getElementById('remove-all-btn').addEventListener('click', async () => {
        if (confirm('Are you sure to remove all tickers?')) {
            const response = await fetch('/remove_all_tickers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            if (response.ok) {
                document.getElementById('tickers-body').innerHTML = '';
                tickers = [];
                alert(result.message);
            }
            else {
                alert('Failed to remove all tickers.')
            }
        }
    })

    startUpdateCycle();
});

async function getAllSymbols() {
    const response = await fetch('/get_all_symbols', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        const symbols = await response.json();
        return symbols;
    }
}

async function updatePrices() {
    const tickers = await getAllSymbols();

    for (const ticker of tickers) {
        const response = await fetch('/get_ticker_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'ticker': ticker})
        });

        const data = await response.json();
        const volume = data.volume;
        document.getElementById(`${ticker}-v`).textContent = `${volume}`;
        
        const formatCurrentPrice = (Math.abs(data.currentPrice) < 0.1) ? data.currentPrice.toPrecision(3) : data.currentPrice.toFixed(2);
        document.getElementById(`${ticker}-price`).textContent = `$${formatCurrentPrice}`;
        
        const percentChange = (((data.currentPrice - data.openPrice) / data.openPrice) * 100).toFixed(2);
        const percentChangePrefix = percentChange > 0 ? '+' : '';
        document.getElementById(`${ticker}-pct`).textContent = `${percentChangePrefix}${percentChange}%`;
        
        const priceChange = (data.currentPrice - data.openPrice);
        const formatPriceChange = (Math.abs(priceChange) < 0.1) ? priceChange.toPrecision(2) : priceChange.toFixed(2);
        const priceChangePrefix = priceChange > 0 ? '+' : '';
        document.getElementById(`${ticker}-pc`).textContent = `${priceChangePrefix}${formatPriceChange}`;

        let colorClass;

        if (percentChange < 0)
            colorClass = 'red';
        else if (percentChange == 0)
            colorClass = 'gray';
        else 
            colorClass = 'green';

        const priceElement = document.getElementById(`${ticker}-price`);
        const pctElement = document.getElementById(`${ticker}-pct`);
        const pcElement = document.getElementById(`${ticker}-pc`);
        priceElement.className = colorClass;
        pctElement.className = colorClass;
        pcElement.className = colorClass;

        let animationClass;
        if (lastPrices[ticker] > data.currentPrice)
            animationClass = 'red-flash';
        else if (lastPrices[ticker] < data.currentPrice)
            animationClass = 'green-flash';
        else
            animationClass = 'gray-flash';

        lastPrices[ticker] = data.currentPrice;

        const tickerElement = document.getElementById(ticker);
        tickerElement.classList.add(animationClass);
        setTimeout(() => {
            tickerElement.classList.remove(animationClass);
        }, 500);
    }
}

function addTickerToGrid(ticker) {
    const tickerBody = document.getElementById('tickers-body');
    const tickerRow = document.createElement('tr');
    tickerRow.id = ticker;
    tickerRow.className = 'ticker-row';
    tickerRow.innerHTML = `
        <td>${ticker}</td>
        <td id="${ticker}-price"></td>
        <td id="${ticker}-pc"></td>
        <td id="${ticker}-pct"></td>
        <td id="${ticker}-v"></td>
        <td><button class="remove-btn" data-ticker="${ticker}">Remove</button></td>`;
    tickerBody.appendChild(tickerRow);
}