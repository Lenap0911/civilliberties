// Initialize jvm namespace if it doesn't exist
if (typeof window.jvm === 'undefined') {
    window.jvm = {
        Map: function(params) {
            var map = this;
            var container = params.container;
            
            // Set container size
            container.style.width = params.width || '100%';
            container.style.height = params.height || '100%';
            
            // Create SVG element
            var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', '100%');
            container.appendChild(svg);
            
            // Create map paths
            var mapData = window.jvm.maps[params.map];
            if (!mapData) {
                console.error('Map data not found:', params.map);
                return;
            }
            
            Object.keys(mapData.paths).forEach(function(code) {
                var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', mapData.paths[code]);
                path.setAttribute('data-code', code);
                
                // Set default style
                path.style.fill = '#e4e4e4';
                path.style.stroke = '#ffffff';
                path.style.strokeWidth = '1';
                
                // Add hover effect
                path.addEventListener('mouseover', function() {
                    this.style.fill = '#cccccc';
                });
                path.addEventListener('mouseout', function() {
                    this.style.fill = '#e4e4e4';
                });
                
                // Add click handler
                if (params.onRegionClick) {
                    path.addEventListener('click', function() {
                        params.onRegionClick.call(this, null, code);
                    });
                }
                
                svg.appendChild(path);
            });
            
            // Apply colors from series if provided
            if (params.series && params.series.regions) {
                params.series.regions.forEach(function(region) {
                    Object.keys(region.values).forEach(function(code) {
                        var path = svg.querySelector('[data-code="' + code + '"]');
                        if (path) {
                            var value = region.values[code];
                            var color = getColor(value, region.min, region.max, region.scale);
                            path.style.fill = color;
                        }
                    });
                });
            }
        },
        maps: {}
    };
}

if (!window.jvm.maps) {
    window.jvm.maps = {};
}

// Helper function to get color based on value
function getColor(value, min, max, scale) {
    var ratio = (value - min) / (max - min);
    var startColor = scale[0];
    var endColor = scale[1];
    
    // Simple linear interpolation between two colors
    var r = Math.round(parseInt(startColor.slice(1,3), 16) * (1-ratio) + parseInt(endColor.slice(1,3), 16) * ratio);
    var g = Math.round(parseInt(startColor.slice(3,5), 16) * (1-ratio) + parseInt(endColor.slice(3,5), 16) * ratio);
    var b = Math.round(parseInt(startColor.slice(5,7), 16) * (1-ratio) + parseInt(endColor.slice(5,7), 16) * ratio);
    
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

// Add the map data
window.jvm.maps['europe'] = {
  "width": 950,
  "height": 650,
  "paths": {
    "fr": "M466.3,321.5l-1.7,4.1l-2.4,-1.1l-2.5,-3.4l0.5,-1.3l2.2,-1.3l3.9,3z",
    "de": "M494.3,235.5l1.7,1.9l-0.2,2.2l2.7,2.4l-2.1,2.9l-1.4,4.2l-2.4,1.6l-4.4,-1.1l-0.5,-2.1l-3.4,-1.9l-0.6,-2.4l-2.9,-1.1l3.3,-5.3l2.5,-1.1l0.7,-2.6l2.5,-1.3l1.7,0.8l0.9,2.4l2.9,-0.3z",
    "pl": "M529.3,246.4l-1.6,-3.1l0.5,-2.7l-2.8,-2.5l-5.7,-1.1l-7.1,-3.1l-2.5,0.7l-2.4,-0.4l-3.8,0.5l-0.5,1.8l-2.8,0.7l-2.7,2.9l0.9,2.5l-0.7,1.6l1.5,3.1l-1.3,1.6l2.5,5.8l3.7,5.4l2.4,-0.9l7.1,-2.8l5.8,-2l4.8,0.4l1.7,-1.1l0.7,-2.7l2.3,-2.1l-0.3,-1.8l2.8,-0.9z",
    "gb": "M444.3,220.4l-1.2,3.4l2.6,-0.9l3.1,0.1l-1.4,3.3l-3.5,3.4l2.4,3.2l-2.7,4.1l3.1,1.9l-0.4,2.8l-2.4,1.8l-3.8,-0.4l-5.4,0.6l-4.1,-5.4l-2.4,-4.2l2.9,-3.8l0.9,-3.9l3.9,0.3l3.7,-3.3z",
    "ie": "M433.7,230.4l-3.1,3.9l-3.7,1.1l1.2,-3.5l-1.2,-3.4l4.2,-3.8l3.1,1.9l-0.5,3.8z",
    "es": "M449.3,334.5l-2.9,2.1l-3.7,-0.1l-3.1,1.1l-2.9,-0.3l-2.9,-2.1l-3.3,-0.4l-1.9,1.6l-4.2,0.4l-3.3,-2.7l1.2,-3.1l-1,-3.9l-2.7,-0.4l-1.7,-2.1l1.5,-1.9l-1.4,-1.7l1.7,-4.1l3.9,-0.3l0.9,-2.1l3.9,-0.3l3.1,0.3l2.9,2.5l3.1,-0.3l1.5,3.7l3.1,0.3l2.9,-0.3l2.9,1.7l0.4,2.1l-2.1,2.7l2.1,1.9l-0.4,4.1l0.4,2.1z",
    "pt": "M432.2,329.4l-2.1,2.3l-2.9,-0.9l-2.7,0.7l0.4,-4.7l0.9,-2.3l0.1,-2.7l2.9,-0.7l1.1,2.1l2.4,0.1l-0.1,6.1z",
    "it": "M485.3,337.4l3.9,1l-0.3,2.7l1.5,3.7l-2.1,1.9l-3.1,-0.3l-2.9,-2.1l-0.4,-2.1l1.7,-1.9l1.7,-2.9z",
    "ch": "M481.3,291.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "at": "M502.3,291.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "cz": "M502.3,271.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "sk": "M522.3,271.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "hu": "M522.3,291.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "si": "M502.3,311.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "hr": "M502.3,331.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "ro": "M542.3,291.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "bg": "M542.3,311.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "gr": "M542.3,331.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "ee": "M542.3,211.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "lv": "M542.3,231.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "lt": "M542.3,251.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "be": "M462.3,271.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "nl": "M462.3,251.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "dk": "M482.3,231.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "se": "M502.3,191.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "fi": "M522.3,171.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "cy": "M562.3,371.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "mt": "M492.3,371.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z",
    "lu": "M472.3,271.4l-0.3,1.9l1.7,1.9l-1.7,2.9l-2.1,0.7l-3.1,-1.9l-1.7,-2.9l0.4,-2.1l2.9,-0.7l3.9,0.2z"
  }
}; 