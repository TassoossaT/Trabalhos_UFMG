window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            return {
                weight: 2,
                opacity: 0,
                color: 'white',
                dashArray: '1',
                fillOpacity: 0,
                fillColor: feature.properties['color']
            };
        }

    }
});