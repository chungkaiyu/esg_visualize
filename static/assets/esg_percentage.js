var myChart = echarts.init(document.getElementById('main'));

var option = {
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '5%',
    left: 'center'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '20',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 1048, name: 'Environment' },
        { value: 735, name: 'Social' },
        { value: 580, name: 'Governance' }
      
      ]
    },
    {
      name: 'Access From',
      type: 'pie',
      radius: ['20%', '50%'],
      avoidLabelOverlap: false,
      label: {
        show: true,
        position: 'inner',
        formatter: function (p) {
        //指示线对应文字，说明文字
                      return p.percent.toFixed(0) + "%\n"+ p.data.name;
                    }
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '20',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 1048, name: 'Environment' },
        { value: 735, name: 'Social' },
        { value: 580, name: 'Governance' }
    
      ]
    }
    
  ]
};

myChart.setOption(option);