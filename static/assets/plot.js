// 基于準備好的dom，初始化echarts實例
var myChart = echarts.init(document.getElementById('main'));
// 指定圖表的配置項和數據
/* 

所有如果要產生不同檔案的圖，改這部分就好了([year, MinMaxScalar, Weight, keyIssue])
const E=[[2018, 1.0, 37.1341, 'Carbon Emissions'], [2018, 0.9498779634006246, 35.838300000000004, 'Product Carbon Footprint'], [2018, 0.9429232310495148, 35.6585, 'Toxic Emissions and Waste'], [2019, 1.0, 866.3738999999999, 'Opportunities in Green Building'], [2019, 0.7772352633632486, 711.8776, 'Toxic Emissions and Waste'], [2019, 0.6883344325246035, 650.2212999999999, 'Raw Material Sourcing'], [2020, 1.0, 861.9381, 'Opportunities in Green Building'], [2020, 0.855848655197746, 759.5696999999999, 'Toxic Emissions and Waste'], [2020, 0.8461855623067562, 752.7075, 'Product Carbon Footprint']];
const S=[[2018, 1.0, 48.01759999999999, 'Labor Management'], [2018, 0.9119567047373884, 44.7753, 'Controversial Sourcing'], [2018, 0.8376020333349632, 42.03710000000001, 'Product Safety and Quality'], [2019, 1.0, 1558.915, 'Labor Management'], [2019, 0.4964881386837696, 839.1958, 'Product Safety and Quality'], [2019, 0.4342466521062318, 750.2279000000001, 'Health and Safety'], [2020, 1.0, 2071.7124, 'Labor Management'], [2020, 0.4682200768227308, 1070.8083, 'Health and Safety'], [2020, 0.4222836498984447, 984.3478, 'Product Safety and Quality']];
const G=[[2018, 1.0, 30.794500000000003, 'Ownership and Control'], [2018, 0.8004799267941279, 26.695400000000003, 'Accounting'], [2018, 0.7161228145321444, 24.962300000000003, 'Pay'], [2019, 1.0, 708.9277000000002, 'Business Ethics'], [2019, 0.4999586745828848, 391.3003000000001, 'Accounting'], [2019, 0.4570121991057022, 364.0206, 'Ownership and Control'], [2020, 1.0, 489.7912, 'Business Ethics'], [2020, 0.8551332210536973, 431.3953000000001, 'Accounting'], [2020, 0.7682271452269869, 396.3634, 'Ownership and Control']];

*/
var E=[[]];
var S=[[]];
var G=[[]];

const itemStyle = {
opacity: 0.8,
shadowBlur: 10,
shadowOffsetX: 0,
shadowOffsetY: 0,
shadowColor: 'rgba(0,0,0,0.3)'
};
var option = {
    color: ['#99EEC1', '#99B5EE', '#EE9F99'],
    legend: {
        top: 10,
        data: ['Environment','Social', 'Governance'],
        textStyle: {
        fontSize: 16
        }
    },
    grid: {
        left: '10%',
        right: 150,
        top: '18%',
        bottom: '10%'
    },
    tooltip: {
        backgroundColor: 'rgba(255,255,255,0.7)',
        formatter: function (param) {
        var value = param.value;
        // prettier-ignore
        return '<div style="border-bottom: 1px solid rgba(255,255,255,.3); font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">'
                    + value[3] 
                    + '</div>'
                    + 'Relevance Level' + '：' + value[0] + '<br>'
                    + 'Similarity' + '：' + value[1] + '<br>'
                    +'Count: '+value[2]+'<br>'
                    +'Doc_word: '+value[5]+'<br>'
                    +'Pillar: ' +value[4];
        }
    },
    xAxis: {
        type:'value',
        name: 'Relevance Level',
        nameGap: 16,
        nameTextStyle: {
        fontSize: 16
        },
        splitLine: {
        show: false
        }
    },
    yAxis: {
        type: 'value',
        name: 'Average Similarity of Word Use in Key Issue',
        min:0.5,
        nameTextStyle: {
        fontSize: 16
        }
    },
    visualMap: [
        {
        left: 'right',
        top: '10%',
        dimension: 2,
        calculable: true,
        precision: 0.000000001,
        text: ['圓形大小：(Count)'],
        textGap: 30,
        inRange: {
            symbolSize: [10, 70]
        },
        outOfRange: {
            symbolSize: [10, 70],
            color: ['rgba(255,255,255,0.4)'],
        },
        controller: {
            inRange: {
            color: ['#BEBEBE']
            },
            outOfRange: {
            color: ['#999']
            }
        }
        },
    ],
    series: [
        {
            name: 'Environment',
            type: 'scatter',
            itemStyle: itemStyle,
            data: E
      
        },
        {
            name: 'Social',
            type: 'scatter',
            itemStyle: itemStyle,
            data: S,
            },
        {
        name: 'Governance',
        type: 'scatter',
        itemStyle: itemStyle,
        data: G,
    }
    ],label:{
        show:false,
        position: 'inside',
        color:'black',
        formatter:function(params){
            return params.data[3]
        }
      }
};
myChart.setOption(option);

function changeESG(data) {
    option['series'][0]['data'] = data.E;
    option['series'][1]['data'] = data.S;
    if(typeof data.G == typeof data.E){
        option['series'][2]['data'] = data.G;
        max=0
        for(var v in data.E){
            if(data.E[v][2]>max)max=data.E[v][2]
        }
        for(var v in data.S){
            if(data.S[v][2]>max)max=data.S[v][2]
        }
        for(var v in data.G){
            if(data.G[v][2]>max)max=data.G[v][2]
        }
    }
    else{
        max=0
        for(var v in data.E){
            if(data.E[v][2]>max)max=data.E[v][2]
        }
        for(var v in data.S){
            if(data.S[v][2]>max)max=data.S[v][2]
        }
        option.series[0].name=data.G
        option.series[1].name='Applied'
        option.color=['#ADD8E6', '#FFB6C1']
        option.legend.data=[data.G,'Applied']
    }
    option.visualMap[0].max=max
    myChart.setOption(option);
}

$.ajax({
    url: "/updateESG",
    dataType: 'json',
    success: function(data){ 
        changeESG(data);
    }
});

$("#SwitchCheck").click( function () {
    if($("#SwitchCheck:checked").length==1){
        option.label.show=true;
        myChart.setOption(option);
    }
    else{
        option.label.show=false;
        myChart.setOption(option);
    }
});