document.addEventListener('DOMContentLoaded', (event) => {
    const checkboxes = document.querySelectorAll('.form-check-input');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', (event) => {
            if (event.target.checked) {
                event.target.parentNode.classList.add('active');
            } else {
                event.target.parentNode.classList.remove('active');
            }
        });
    });
});

var coll = document.getElementsByClassName("collapsible");
for (var i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
  const dataContainer = document.getElementById('data-container');
  
  const accountResult = JSON.parse(dataContainer.getAttribute('data-account-result'));
  const baselineResult = JSON.parse(dataContainer.getAttribute('data-baseline-result'));
  const decisionArray = JSON.parse(dataContainer.getAttribute('data-decision-array'));
  const profit = parseFloat(dataContainer.getAttribute('data-profit'));
  const maxLoss = parseFloat(dataContainer.getAttribute('data-max-loss'));

  const ctx = document.getElementById('backward_test_result_chart').getContext('2d');
  const chart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: accountResult.map((_, index) => index),
          datasets: [{
              label: 'Account Result',
              data: accountResult,
              borderColor: 'blue',
              backgroundColor: 'transparent',
              fill: false,
          }, {
              label: 'Baseline Result',
              data: baselineResult,
              borderColor: 'red',
              backgroundColor: 'transparent',
              fill: false,
          }]
      },
      options: {
          scales: {
              x: {
                  type: 'linear',
                  position: 'bottom'
              }
          }
      }
  });
});