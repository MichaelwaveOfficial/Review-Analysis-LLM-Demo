document.addEventListener("DOMContentLoaded", function () {
    fetch('/gdb_data')
    .then(response => response.json())
    .then(data => {
        const nodes = new vis.DataSet(data.nodes)
        const edges = new vis.DataSet(data.edges)
    
        const container = document.getElementById('gdb')
        const dataNetwork = {
            nodes: nodes, 
            edges: edges
        }
    
        const options = {
            nodes: {
                shape: 'dot',
                size: 15,
                font: {
                    size:14,
                    color: data.sentiment === 'Negative' ? 'red' : 'green' // Nodes colour depends on sentiment.
                }
            },
            edges: {
                arrows: 'to',
                font: {
                    align: 'middle'
                }
            },
            layout: {
                improvedLayout: true
            },
            physics: {
                stabilization: true
            }
        }
        new vis.Network(container, dataNetwork, options)
    })
})
