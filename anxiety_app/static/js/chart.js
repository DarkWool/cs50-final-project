const data = {
    labels: labels,
    datasets: [{
        label: 'Result',
        data: categoriesResults,
        backgroundColor: [
            'hsla(323, 90%, 58%, .2)',
            'hsla(42, 100%, 50%, .2)',
            'hsla(178, 60%, 32%, .2)',
            'hsla(256, 100%, 50%, .2)',
            'hsla(248, 34%, 17%, .2)',
            'hsla(210, 12%, 29%, .2)',
        ],
        borderColor: [
            'hsl(323, 90%, 58%)',
            'hsl(42, 100%, 50%)',
            'hsl(178, 60%, 32%)',
            'hsl(256, 100%, 50%)',
            'hsl(248, 34%, 17%)',
            'hsl(210, 12%, 29%)',
        ],
        borderWidth: 2
    }]
};

const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    callback: function (value) {
                        return value + "%";
                    }
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let label = context.dataset.label || '';

                        if (label) {
                            return label += `:  ${context.parsed.y}%`;
                        } 
                    }
                }
            }
        }
    },
};

const myChart = new Chart(
    document.getElementById('barChart'),
    config
);