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
        scaleStepWidth : 20,
        scaleStartValue : -100,
        animation: true
    };
    var ctx = canvasElement.getContext('2d');
    var sentimentChart = new Chart(ctx).Line(data, options);
}

function createDataset(data) {
    return {
        label: data.key + " sentiment",
        data: _.map(data.sentiments, function(element) {
            return element.value;
        }),
        fillColor: "rgba(50,180,220,0.2)",
        strokeColor: "rgba(50,180,220,1)",
        pointColor: "rgba(50,180,220,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(50,180,220,1)"
    }
}

function createLabels(data) {
    return _.map(data.sentiments, function(element) {
        return new Date(element.created_date).toDateString();
    });
}
