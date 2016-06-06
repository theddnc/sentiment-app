/**
 * Created by jzaczek on 09.04.2016.
 */

$( document ).ready(function() {
    var keyword_url = window.location.href;
    keyword_url = keyword_url.replace('ui', 'api');

    var chartCanvas = document.getElementById('sentiment-chart');
    if (chartCanvas) {
        $.get(keyword_url).then(function(result) {
           createChart(result, chartCanvas);
        });
    }
});

function createChart(apiResult, canvasElement) {
    var data = {
            labels: createLabels(apiResult),
            datasets: [createDataset(apiResult)]
    };
    var options = {
        scaleOverride : true,
        scaleSteps : 10,
        scaleStepWidth : 2,
        scaleStartValue : -10,
        tooltips: {
            callbacks: {
                label: function(tooltipItem, data) {
                    return data.datasets[0].tweets[tooltipItem.index].split(' ').slice(0, 10).join(' ') + '...';
                }
            }
        }
    };
    var ctx = canvasElement.getContext('2d');
    var sentimentChart = new Chart(ctx, {
        data: data,
        options: options,
        type: 'line'
    });
}

function createDataset(data) {
    return {
        label: data.key + " sentiment",
        data: _.map(data.sentiments, function(element) {
            return element.value;
        }),
        tweets: _.map(data.sentiments, function(element) {
            return element.tweet.text;
        }),
        backgroundColor: "rgba(50,180,220,0.2)",
        borderColor: "rgba(50,180,220,1)"
    }
}

function createLabels(data) {
    return _.map(data.sentiments, function(element, idx) {
        var date = new Date(element.created_date);
        return date.toDateString() + ' ' + date.toTimeString().split(' ')[0];
    });
}
