var min = 10;
$.get('/api/stats?minutes=' + min, function(data) {
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

var Header = React.createClass({
    render: function() {
        return (
            <div>
                <p>Network Traffic for the last {this.props.minutes} minute(s)</p>
            </div>
        )
    }
})

var header = <Header minutes={min} />;

ReactDOM.render(
    header,
    document.getElementById('container')
);
