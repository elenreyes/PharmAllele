window.addEventListener('DOMContentLoaded', event => {

    // --- 1. CONFIGURACIÓN DE LA TABLA (DataTables) ---
    // Inicializamos la tabla para que cuando Elena la cargue, ya tenga buscador y paginación
    const table = $('#table-output').DataTable({
        language: { url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/es-ES.json' },
        responsive: true,
        columns: [
            { title: "Gene" },
            { title: "Variant" },
            { title: "Drug" },
            { title: "Significance" }
        ]
    });

    // --- 2. LÓGICA DE BÚSQUEDA ---
    const searchForm = document.querySelector('.search-panel');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Evita que la página se refresque

            // Capturamos lo que escribió el usuario en el HTML de Elena
            const gene = document.querySelector('input[name="gene"]').value;
            const variant = document.querySelector('input[name="variant"]').value;
            const drug = document.querySelector('input[name="drug"]').value;

            // Validación simple: Si todo está vacío, avisamos
            if (!gene && !variant && !drug) {
                alert("Por favor, rellena al menos un campo para buscar.");
                return;
            }

            console.log("Buscando datos para:", {gene, variant, drug});
            
            // Llamamos a la función que pide los datos al servidor
            ejecutarBusqueda(gene, variant, drug);
        });
    }

    // --- 3. FUNCIÓN FETCH (Conexión con MySQL vía PHP/Python) ---
    function ejecutarBusqueda(g, v, d) {
        // Aquí conectamos con el backend. Por ahora usamos datos de prueba (Mock)
        // para que veas cómo funciona antes de tener el MySQL listo.
        
        const datosPrueba = [
            {gene: g || "CYP2D6", variant: v || "∗4", drug: d || "Tamoxifen", significance: "High"},
            {gene: g || "VKORC1", variant: v || "rs9923231", drug: d || "Warfarin", significance: "Medium"}
        ];

        // Simulamos que el servidor tarda un poco y nos devuelve los datos
        actualizarPantalla(datosPrueba);
    }

    // --- 4. ACTUALIZAR TABLA Y GRÁFICO ---
    function actualizarPantalla(datos) {
        // Actualizar Tabla
        table.clear();
        datos.forEach(item => {
            table.row.add([item.gene, item.variant, item.drug, item.significance]);
        });
        table.draw();

        // Actualizar Gráfico de Plotly
        const traces = [{
            x: datos.map(d => d.drug),
            y: [10, 20], // Aquí pondrías valores reales de tu DB
            type: 'bar',
            marker: { color: '#1abc9c' }
        }];

        Plotly.newPlot('myDiv', traces, { title: 'Resultados de Farmacogenética' });
        
        alert("¡Datos actualizados!");
    }

    // --- 5. LÓGICA DEL TEMPLATE (Freelancer) ---
    // Esto hace que el menú cambie al hacer scroll
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) return;
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }
    };
    navbarShrink();
    document.addEventListener('scroll', navbarShrink);

});