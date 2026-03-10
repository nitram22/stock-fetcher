async function load(){

const res = await fetch("../data/dashboard.json")

const data = await res.json()

document.getElementById("value").innerText =
"Portfolio Value: $" + data.portfolio_value.toFixed(2)


function render(id, rows){

const table = document.getElementById(id)

table.innerHTML = ""

rows.forEach(r => {

const tr = document.createElement("tr")

tr.innerHTML = `
<td>${r.ticker}</td>
<td>${r.price.toFixed(2)}</td>
<td>${r.change_percent.toFixed(2)}%</td>
<td>${r.impact.toFixed(2)}</td>
`

table.appendChild(tr)

})

}

render("radar", data.movement_radar)

render("gainers", data.gainers)

render("losers", data.losers)

render("impact", data.impact_rank)

render("stocks", data.stocks)

}

load()