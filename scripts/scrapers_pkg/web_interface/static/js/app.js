// Main JavaScript for the scraper dashboard

// Global variables
let scrapingStatusInterval;
let dbStatusInterval;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    checkDatabaseStatus();
    
    // Set up periodic status checks
    dbStatusInterval = setInterval(checkDatabaseStatus, 30000); // Every 30 seconds
    
    // Check if scraping is running and start monitoring
    checkScrapingStatus();
});

// Initialize dashboard functionality
function initializeDashboard() {
    // Add click handlers for quick actions
    const quickActionButtons = document.querySelectorAll('[onclick*="startScraper"]');
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.disabled) {
                e.preventDefault();
                showNotification('A scraper is already running', 'warning');
            }
        });
    });
    
    // Add loading states to buttons
    const allButtons = document.querySelectorAll('button[onclick]');
    allButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                addLoadingState(this);
            }
        });
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Check database connection status
function checkDatabaseStatus() {
    fetch('/api/test_connection')
        .then(response => response.json())
        .then(data => {
            updateDatabaseStatus(data.success);
        })
        .catch(error => {
            console.error('Error checking database status:', error);
            updateDatabaseStatus(false);
        });
}

// Update database status indicator
function updateDatabaseStatus(isConnected) {
    const statusElement = document.getElementById('db-status-text');
    if (statusElement) {
        if (isConnected) {
            statusElement.innerHTML = '<span class="text-success">Connected</span>';
        } else {
            statusElement.innerHTML = '<span class="text-danger">Disconnected</span>';
        }
    }
}

// Check scraping status
function checkScrapingStatus() {
    fetch('/api/scraping_status')
        .then(response => response.json())
        .then(data => {
            updateScrapingStatus(data);
            
            // If scraping is running, start monitoring
            if (data.is_running && !scrapingStatusInterval) {
                startScrapingMonitor();
            } else if (!data.is_running && scrapingStatusInterval) {
                stopScrapingMonitor();
            }
        })
        .catch(error => {
            console.error('Error checking scraping status:', error);
        });
}

// Start monitoring scraping progress
function startScrapingMonitor() {
    scrapingStatusInterval = setInterval(function() {
        fetch('/api/scraping_status')
            .then(response => response.json())
            .then(data => {
                updateScrapingStatus(data);
                
                // If scraping completed, reload page to show results
                if (!data.is_running) {
                    stopScrapingMonitor();
                    showNotification('Scraping completed!', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error monitoring scraping:', error);
            });
    }, 3000); // Check every 3 seconds
}

// Stop monitoring scraping progress
function stopScrapingMonitor() {
    if (scrapingStatusInterval) {
        clearInterval(scrapingStatusInterval);
        scrapingStatusInterval = null;
    }
}

// Update scraping status display
function updateScrapingStatus(status) {
    // Update progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        bar.style.width = status.progress + '%';
        bar.setAttribute('aria-valuenow', status.progress);
    });
    
    // Update status text
    const statusTexts = document.querySelectorAll('.scraping-status-text');
    statusTexts.forEach(text => {
        if (status.is_running) {
            text.textContent = `Running: ${status.current_brand} (${status.progress}%)`;
        } else {
            text.textContent = 'Idle';
        }
    });
    
    // Update last update time
    const lastUpdateElements = document.querySelectorAll('#last-update');
    lastUpdateElements.forEach(element => {
        if (status.last_update) {
            const date = new Date(status.last_update);
            element.textContent = date.toLocaleTimeString();
        }
    });
    
    // Enable/disable buttons based on scraping status
    const scraperButtons = document.querySelectorAll('button[onclick*="startScraper"]');
    scraperButtons.forEach(button => {
        button.disabled = status.is_running;
    });
    
    const stopButtons = document.querySelectorAll('button[onclick*="stopScraper"]');
    stopButtons.forEach(button => {
        button.disabled = !status.is_running;
    });
}

// Add loading state to button
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
    button.disabled = true;
    
    // Remove loading state after 3 seconds (fallback)
    setTimeout(() => {
        removeLoadingState(button, originalText);
    }, 3000);
}

// Remove loading state from button
function removeLoadingState(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    if (seconds < 60) {
        return seconds + 's';
    } else if (seconds < 3600) {
        return Math.floor(seconds / 60) + 'm ' + (seconds % 60) + 's';
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return hours + 'h ' + minutes + 'm';
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

// Export data functionality
function exportData(format = 'json') {
    fetch('/api/products?limit=1000')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let content, filename, mimeType;
                
                if (format === 'json') {
                    content = JSON.stringify(data.products, null, 2);
                    filename = 'scraped_products.json';
                    mimeType = 'application/json';
                } else if (format === 'csv') {
                    content = convertToCSV(data.products);
                    filename = 'scraped_products.csv';
                    mimeType = 'text/csv';
                }
                
                downloadFile(content, filename, mimeType);
                showNotification(`Data exported as ${format.toUpperCase()}`, 'success');
            } else {
                showNotification('Failed to export data', 'danger');
            }
        })
        .catch(error => {
            console.error('Export error:', error);
            showNotification('Export failed', 'danger');
        });
}

function convertToCSV(data) {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header];
                // Handle arrays and objects
                if (Array.isArray(value)) {
                    return `"${value.join('; ')}"`;
                } else if (typeof value === 'object' && value !== null) {
                    return `"${JSON.stringify(value)}"`;
                } else {
                    return `"${String(value).replace(/"/g, '""')}"`;
                }
            }).join(',')
        )
    ].join('\n');
    
    return csvContent;
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (scrapingStatusInterval) {
        clearInterval(scrapingStatusInterval);
    }
    if (dbStatusInterval) {
        clearInterval(dbStatusInterval);
    }
});
