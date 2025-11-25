// Product Availability Report functionality

// Global chart references
let productAvailabilityChart = null;
let productByRegionChart = null;

// Load Product Availability Report
function loadProductAvailabilityReport() {
    showReportLoader('productAvailabilityReport');
    
    fetch('/reports/product_availability')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch product availability data');
            }
            return response.json();
        })
        .then(data => {
            hideReportLoader('productAvailabilityReport');
            createProductAvailabilityElements();
            displayProductAvailability(data);
        })
        .catch(error => {
            hideReportLoader('productAvailabilityReport');
            showReportError('productAvailabilityReport', error.message);
            console.error('Error fetching product availability data:', error);
        });
}

// Create canvas elements for product availability report
function createProductAvailabilityElements() {
    const reportContainer = document.getElementById('productAvailabilityReport');
    
    // Check if elements already exist
    if (document.getElementById('productAvailabilityChart') && 
        document.getElementById('productByRegionChart') &&
        document.getElementById('productBreakdownTableBody')) {
        return;
    }
    
    // Create report structure
    reportContainer.innerHTML = `
        <div class="row mb-4">
            <div class="col-md-6 mb-4">
                <div class="chart-container">
                    <canvas id="productAvailabilityChart"></canvas>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="chart-container">
                    <canvas id="productByRegionChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Product Breakdown Table -->
        <div class="table-responsive">
            <table class="table table-sm table-bordered">
                <thead class="table-light">
                    <tr>
                        <th>Product</th>
                        <th>SW</th>
                        <th>SE</th>
                        <th>NC</th>
                        <th>NW</th>
                        <th>NE</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody id="productBreakdownTableBody">
                    <!-- Table content will be populated by JavaScript -->
                </tbody>
            </table>
        </div>
    `;
}

function displayProductAvailability(data) {
    // Product Availability Chart
    const canvasId1 = 'productAvailabilityChart';
    const canvas1 = document.getElementById(canvasId1);
    if (!canvas1) {
        console.error(`Canvas element with ID '${canvasId1}' not found`);
        return;
    }
    
    const productLabels = Object.keys(data.product_stats);
    const availableCounts = productLabels.map(product => data.product_stats[product].available);
    const notAvailableCounts = productLabels.map(product => data.product_stats[product].not_available);
    
    // Safely destroy existing chart
    if (productAvailabilityChart) {
        try {
            productAvailabilityChart.destroy();
        } catch (error) {
            console.warn('Error destroying product availability chart:', error);
        }
    }
    
    // Create new chart
    try {
        const ctx1 = canvas1.getContext('2d');
        productAvailabilityChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: productLabels,
                datasets: [
                    {
                        label: 'Available',
                        data: availableCounts,
                        backgroundColor: 'rgba(75, 192, 192, 0.8)',
                        borderWidth: 1
                    },
                    {
                        label: 'Not Available',
                        data: notAvailableCounts,
                        backgroundColor: 'rgba(255, 99, 132, 0.8)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Product Availability Across All Outlets',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating product availability chart:', error);
    }
    
    // Product by Region Chart
    const canvasId2 = 'productByRegionChart';
    const canvas2 = document.getElementById(canvasId2);
    if (!canvas2) {
        console.error(`Canvas element with ID '${canvasId2}' not found`);
        return;
    }
    
    const regions = Object.keys(data.product_by_region);
    
    // Calculate availability percentage by region
    const availabilityByRegion = regions.map(region => {
        let totalAvailable = 0;
        let totalProducts = 0;
        
        Object.keys(data.product_by_region[region]).forEach(product => {
            totalAvailable += data.product_by_region[region][product].available;
            totalProducts += data.product_by_region[region][product].available + 
                          data.product_by_region[region][product].not_available;
        });
        
        return (totalAvailable / totalProducts) * 100;
    });
    
    // Safely destroy existing chart
    if (productByRegionChart) {
        try {
            productByRegionChart.destroy();
        } catch (error) {
            console.warn('Error destroying product by region chart:', error);
        }
    }
    
    // Create new chart
    try {
        const ctx2 = canvas2.getContext('2d');
        productByRegionChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: regions,
                datasets: [{
                    label: 'Product Availability (%)',
                    data: availabilityByRegion,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Product Availability by Region',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating product by region chart:', error);
    }
    
    // Update table with breakdown by product and region
    populateProductBreakdownTable(data);
}