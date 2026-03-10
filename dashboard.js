document.addEventListener('DOMContentLoaded', () => {
  fetch('dashboard.json')
    .then(res => res.json())
    .then(data => {
      function fillTable(id, items, cls) {
        const tableElem = document.getElementById(id);
        if (!tableElem) return;
        const tbody = tableElem.querySelector('tbody');
        tbody.innerHTML = '';

        if (!items || items.length === 0) {
          tbody.innerHTML = '<tr><td colspan="3">No data yet</td></tr>';
          return;
        }

        items.forEach(item => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${item.ticker}</td>
            <td>${item.last_price.toFixed(2)}</td>
            <td class="${cls}">${item.change_percent.toFixed(2)}%</td>
          `;
          tbody.appendChild(row);
        });
      }

      fillTable('gainers', data.gainers, 'gain');
      fillTable('losers', data.losers, 'loss');
    })
    .catch(err => {
      console.error('Error loading dashboard:', err);
      const gainers = document.getElementById('gainers')?.querySelector('tbody');
      const losers = document.getElementById('losers')?.querySelector('tbody');
      if (gainers) gainers.innerHTML = '<tr><td colspan="3">No data yet</td></tr>';
      if (losers) losers.innerHTML = '<tr><td colspan="3">No data yet</td></tr>';
    });
});