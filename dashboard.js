fetch('dashboard.json')
  .then(res => res.json())
  .then(data => {
    function fillTable(id, items, cls) {
      const tbody = document.getElementById(id).querySelector('tbody');
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
    document.getElementById('gainers').querySelector('tbody').innerHTML =
      '<tr><td colspan="3">No data yet</td></tr>';
    document.getElementById('losers').querySelector('tbody').innerHTML =
      '<tr><td colspan="3">No data yet</td></tr>';
  });