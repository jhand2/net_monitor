$(document).ready(function() {
    $.get('/api/stats?minutes=1', function(data) {
        data = JSON.parse(data);
        Plotly.plot('chart', [{
            x: data.map(function(d) {
                var date = new Date(Math.floor(d.start_time));
                date.setMilliseconds(0);
                return date;
            }),
            y: data.map(function(d) {return d.tcp_per_second}),
            type: 'scatter'
        }]);
    });
});
