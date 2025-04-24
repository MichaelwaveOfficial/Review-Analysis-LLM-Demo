
    
function loadGdb(user_selection) {

    // Query graph relative to user selected option.
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

            // Return node metadata with base styling.
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

        // Fetch container to be styled.
        const container = document.getElementById('gdb')

        // Create dataNetwork obj and pass nodes and their relationships.
        const dataNetwork = {
            nodes: new vis.DataSet(nodes), 
            edges: new vis.DataSet(data.edges)
        }

        // Styling options for the data network.
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

        // Instantiate new network obj.
    new vis.Network(container, dataNetwork, options)

    })
    .catch(error => {
        console.error('Error fetching graph database:', error) // Return error if GDB cannot be loaded.
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
