
    
function loadGdb(user_selection) {

    fetch(`/gdb_data?user_selection=${user_selection}`)
    .then(response => response.json())
    .then(data => {


    const nodes = data.nodes.map(node => {
        
        // Default node colour.
        let colour = 'gray'
        

        // Style Review sentiment nodes. 
        if (node.group === 'Review') {
            if (node.sentiment === 'Negative') {
                colour = 'red'
            } else if (node.sentiment === 'Positive') {
                colour = 'green'
            }
        }

        // Style aspect nodes.
        if (node.group === 'Aspect') {
            colour = 'blue'
        }
        
        // Style entity nodes. 
        if (node.group === 'Entity') {
            colour = 'orange'
        }

        return {
            id: node.id,
            label: node.label,
            title: JSON.stringify(node, null, 2),
            group: node.group,
            color: {
                background: colour,
                border: '#000000'
            }
        }
    })

    const container = document.getElementById('gdb')

    const dataNetwork = {
        nodes: new vis.DataSet(nodes), 
        edges: new vis.DataSet(data.edges)
    }

    const options = {
        nodes: {
            shape: 'dot',
            size: 15,
            font: {
                size:14,
                color: '#000000'
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
    .catch(error => {
        console.error('Error fetching graph database:', error)
    });
}

document.addEventListener('DOMContentLoaded', function() {

    // load default.
    loadGdb('view_all')

    // Add view all function to button.
    document.getElementById('view_all').addEventListener('click', function() { loadGdb('view_all') })

    // Add reviews aspects function to button.
    document.getElementById('review_aspects').addEventListener('click', function(){ loadGdb('review_aspects') })

    document.getElementById('review_entities').addEventListener('click', function() { loadGdb('review_entities') })
})

