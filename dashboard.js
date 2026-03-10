fetch("dashboard.json")
.then(r=>r.json())
.then(data=>{

document.getElementById("summary").innerHTML =
`Total Value: $${data.total_value.toFixed(2)}`


function fill(id, rows){

const tbody = document.querySelector(`#${id} tbody`)

tbody.innerHTML=""

rows.forEach(r=>{

const tr = document.createElement("tr")

tr.innerHTML = `
<td>${r.ticker}</td>
<td>${r.price.toFixed(2)}</td>
<td>${r.change_percent.toFixed(2)}%</td>
`

tbody.appendChild(tr)

})

}

fill("gainers",data.gainers)
fill("losers",data.losers)
fill("portfolio",data.portfolio)

})