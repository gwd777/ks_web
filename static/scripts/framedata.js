$(function(){
    /*标准*/
    var radar = echarts.init(document.getElementById('radar'));
    var option = {
            title: {
                //text: '出租车/网约车-当日排队长度',
                left: 'center',
                textStyle: {
                    color: '#ffffff',
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            legend: {
                data: ['出租车排队长度', '网约车排队长度'], // 添加网约车排队长度到图例
                top: '40px',
                textStyle: {
                    color: '#ffffff'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: ['0点', '1点', '2点', '3点', '4点', '5点', '6点', '7点', '8点', '9点', '10点', '11点', '12点', '13点', '14点', '15点', '16点', '17点', '18点', '19点', '20点', '21点', '22点', '23点'],
                axisLine: {
                    lineStyle: {
                        color: '#ffffff'
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: '排队长度(辆)',
                axisLine: {
                    lineStyle: {
                        color: '#5470C6'
                    }
                },
                axisLabel: {
                    formatter: '{value} 辆'
                }
            },
            series: [
                {
                    name: '出租车排队长度',
                    type: 'line',
                    data: [15, 20, 25, 30, 28, 35, 40, 45, 40, 57, 60, 65, 90, 75, 88, 85, 99, 95, 99, 95, 95, 85, 80, 75],
                    lineStyle: {
                        color: '#EE6666',
                        width: 3
                    },
                    symbol: 'circle',
                    symbolSize: 10,
                    itemStyle: {
                        color: '#EE6666',
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    },
                    smooth: true // 使线条平滑
                },
                {
                    name: '网约车排队长度',
                    type: 'line',
                    data: [12, 18, 22, 38, 25, 32, 30, 22, 47, 52, 67, 52, 67, 72, 67, 92, 87, 62, 88, 83, 68, 73, 68, 88], // 假设的数据
                    lineStyle: {
                        color: '#00FF00', // 设置不同的颜色以区分
                        width: 3
                    },
                    symbol: 'circle',
                    symbolSize: 10,
                    itemStyle: {
                        color: '#00FF00',
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    },
                    smooth: true // 使线条平滑
                }
            ]
        };
    radar.setOption(option);

    var taxiQueueData =   [20, 65, 30, 35, 25, 28, 30, 25, 20, 75, 30, 25]; // 每月的出租车平均排队长度（单位：辆）
    var netCarQueueData = [15, 70, 25, 35, 21, 33, 35, 19, 25, 60, 25, 20]; // 每月的网约车平均排队长度（单位：辆）
    var graduateyear = echarts.init(document.getElementById('graduateyear'));
    var option = {
        title: {
            // text: '站内出租车/网约车-月平均排队长度',
            left: 'center',
            textStyle: {
                color: '#ffffff',
                fontSize: 18,
                fontWeight: 'bold'
            }
        },
        legend: {
            data: ['出租车平均排队长度', '网约车平均排队长度'], // 添加网约车排队长度到图例
            top: '40px',
            textStyle: {
                color: '#ffffff'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
            axisLine: {
                lineStyle: {
                    color: '#ffffff'
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '平均排队长度',
            axisLine: {
                lineStyle: {
                    color: '#5470C6'
                }
            },
            axisLabel: {
                formatter: '{value} 辆'
            }
        },
        series: [
            {
                name: '出租车平均排队长度',
                type: 'line',
                data: taxiQueueData,
                lineStyle: {
                    color: '#EE6666',
                    width: 3
                },
                symbol: 'circle',
                symbolSize: 10,
                itemStyle: {
                    color: '#EE6666',
                    borderWidth: 2,
                    borderColor: '#ffffff'
                },
                smooth: true // 使线条平滑
            },
            {
                name: '网约车平均排队长度',
                type: 'line',
                data: netCarQueueData, // 使用新的数据集
                lineStyle: {
                    color: '#00FF00', // 设置不同的颜色以区分
                    width: 3
                },
                symbol: 'circle',
                symbolSize: 10,
                itemStyle: {
                    color: '#00FF00',
                    borderWidth: 2,
                    borderColor: '#ffffff'
                },
                smooth: true // 使线条平滑
            }
        ]
    };
    graduateyear.setOption(option);

    var mapadd = echarts.init(document.getElementById('mapadd'));
    var option = {
            title: {
                // text: '轨道交通数据：出租车/网约车-排队长度桑基图',
                left: 'center',
                textStyle: {
                    fontSize: 18,
                    fontWeight: 'bold'
                }
            },
            backgroundColor: '#ffffff',  // 设置酷炫的背景色
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c}'
            },
            series: [
                {
                    name: '排队长度',
                    type: 'sankey',
                    layout: 'none',
                    emphasis: {
                        focus: 'adjacency'
                    },
                    data: [
                        {name: '平均排队长度'},
                        {name: '高峰时段排队长度'},
                        {name: '最大排队长度'},

                        {name: '排队等待时间'},
                        {name: '客流量'},
                        {name: '天气条件'},
                        {name: '节假日'},
                        {name: '特殊事件'},
                        {name: '公交车运营综合指数'},
                        {name: '地铁运营综合指数'},

                        {name: '乘客满意度'},
                        {name: '站内运营管理健康指数'}
                    ],
                    links: [
                        {source: '平均排队长度', target: '排队等待时间', value: 5},
                        {source: '平均排队长度', target: '客流量', value: 3},
                        {source: '平均排队长度', target: '天气条件', value: 2},
                        {source: '平均排队长度', target: '节假日', value: 4},
                        {source: '平均排队长度', target: '特殊事件', value: 4},
                        {source: '平均排队长度', target: '公交车运营综合指数', value: 6},
                        {source: '平均排队长度', target: '地铁运营综合指数', value: 6},

                        {source: '高峰时段排队长度', target: '排队等待时间', value: 15},
                        {source: '高峰时段排队长度', target: '客流量', value: 13},
                        {source: '高峰时段排队长度', target: '天气条件', value: 12},
                        {source: '高峰时段排队长度', target: '节假日', value: 14},
                        {source: '高峰时段排队长度', target: '特殊事件', value: 9},
                        {source: '高峰时段排队长度', target: '公交车运营综合指数', value: 3},
                        {source: '高峰时段排队长度', target: '地铁运营综合指数', value: 7},

                        {source: '最大排队长度', target: '排队等待时间', value: 11},
                        {source: '最大排队长度', target: '客流量', value: 5},
                        {source: '最大排队长度', target: '天气条件', value: 12},
                        {source: '最大排队长度', target: '节假日', value: 24},
                        {source: '最大排队长度', target: '特殊事件', value: 19},
                        {source: '最大排队长度', target: '公交车运营综合指数', value: 3},
                        {source: '最大排队长度', target: '地铁运营综合指数', value: 7},

                        {source: '排队等待时间', target: '乘客满意度', value: 7},
                        {source: '客流量', target: '乘客满意度', value: 1},
                        {source: '天气条件', target: '乘客满意度', value: 8},
                        {source: '节假日', target: '乘客满意度', value: 10},
                        {source: '特殊事件', target: '乘客满意度', value: 11},
                        {source: '公交车运营综合指数', target: '乘客满意度', value: 11},
                        {source: '地铁运营综合指数', target: '乘客满意度', value: 11},

                        {source: '排队等待时间', target: '站内运营管理健康指数', value: 7},
                        {source: '客流量', target: '站内运营管理健康指数', value: 1},
                        {source: '天气条件', target: '站内运营管理健康指数', value: 8},
                        {source: '节假日', target: '站内运营管理健康指数', value: 10},
                        {source: '特殊事件', target: '站内运营管理健康指数', value: 11},
                        {source: '公交车运营综合指数', target: '站内运营管理健康指数', value: 11},
                        {source: '地铁运营综合指数', target: '站内运营管理健康指数', value: 11}
                    ]
                }
            ]
        };
    mapadd.setOption(option);

    /*==*/
    var sexrate = echarts.init(document.getElementById('sexrate'));
    var total = {
        name: '=='
    };
    option = {
        title: [{
            text: total.name,
            left: '48%',
            top: '34%',
            textAlign: 'center',
            textBaseline: 'middle',
            textStyle: {
                color: '#fff',
                fontWeight: 'normal',
                fontSize: 18
            }
        }, {
            text: total.value,
            left: '48%',
            top: '44%',
            textAlign: 'center',
            textBaseline: 'middle',
            textStyle: {
                color: '#fff',
                fontWeight: 'normal',
                fontSize: 18
            }
        }],
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },

        color:['#70a3ff','#ff7f4e'],
        legend: {
            orient: 'vertical',
            x:'center',
            bottom:'5%',
            selectedMode:false,
            formatter:function(name){
                var oa = option.series[0].data;
                var num = oa[0].value + oa[1].value ;
                for(var i = 0; i < option.series[0].data.length; i++){
                    if(name==oa[i].name){
                        return name + "  "+oa[i].value+"  "+ (oa[i].value / num * 100).toFixed(2) + '%';
                    }
                }
            },
            data: ['出租车','网约车'],
            show:true,
            textStyle:{
                color:'#fff',
                fontWeight:'bold'
            },
        },

        series : [
            {
                name: 'PK',
                type: 'pie',
                selectedMode: 'single',
                radius: ['45%', '55%'],
                center: ['50%', '40%'],
                data: [
                    {value: 2629, name: '出租车'},
                    {value: 2507, name: '网约车'}
                ],
                label: {
                    normal: {
                        show: false,
                        position: "outer",
                        align:'left',
                        textStyle: {
                            rotate:true
                        }
                    }
                },
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    },
                    normal: {
                        label:{
                            show: true,
                            formatter: '{b} {c}'
                        }
                    }

                }
            }
        ]
    };
    sexrate.setOption(option);
 
    
    var householdrate = echarts.init(document.getElementById('householdrate'));
    var total = {
        name: '=='
    };
    option = {
        title: [{
            text: total.name,
            left: '48%',
            top: '34%',
            textAlign: 'center',
            textBaseline: 'middle',
            textStyle: {
                color: '#fff',
                fontWeight: 'normal',
                fontSize: 18
            }
        }, {
            text: total.value,
            left: '48%',
            top: '44%',
            textAlign: 'center',
            textBaseline: 'middle',
            textStyle: {
                color: '#fff',
                fontWeight: 'normal',
                fontSize: 18
            }
        }],
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },

        color:['#4f9de7','#4acf79'],
        legend: {
            orient: 'vertical',
            x:'center',
            bottom:'5%',
            selectedMode:false,
            formatter:function(name){
                var oa = option.series[0].data;
                var num = oa[0].value + oa[1].value ;
                for(var i = 0; i < option.series[0].data.length; i++){
                    if(name==oa[i].name){
                        return name + "  "+oa[i].value+"  "+ (oa[i].value / num * 100).toFixed(2) + '%';
                    }
                }
            },
            data: ['出租车','网约车'],
            show:true,
            textStyle:{
                color:'#fff',
                fontWeight:'bold'
            },
        },
        series : [
            {
                name: 'FK',
                type: 'pie',
                selectedMode: 'single',
                radius: ['45%', '55%'],
                center: ['50%', '40%'],
                data: [
                    {value: 2629, name: '出租车'},
                    {value: 2507, name: '网约车'}
                ],
                label: {
                    normal: {
                        show: false,
                        position: "outer",
                        align:'left',
                        textStyle: {
                            rotate:true
                        }
                    }
                },
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    },
                    normal: {
                        label:{
                            show: true,
                            formatter: '{b} {c}'
                        }
                    }
                }
            }
        ]
    };
    householdrate.setOption(option);
   
    /*  =====-=*/
    var courserate = echarts.init(document.getElementById('courserate'));
    var total = {
        name: '=='
    };
    option = {
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            right: '0',
            y:'middle',
            textStyle:{
                color:"#fff"
            },

            formatter:function(name){
                var oa = option.series[0].data;
                var num = oa[0].value + oa[1].value + oa[2].value + oa[3].value+oa[4].value+oa[5].value;
                for(var i = 0; i < option.series[0].data.length; i++){
                    if(name==oa[i].name){
                        return name +  ' '+oa[i].value;
                    }
                }
            },
            data: ['节假日','下雨','排队等待时间','客流量','地铁指数','公交指数']
        },
        series : [
            {
                name: 'FK',
                type: 'pie',
                radius : '45%',
                color:['#27c2c1','#9ccb63','#fcd85a','#60c1de','#0084c8','#d8514b'],
                center: ['38%', '50%'],
                data:[
                    {value:335, name:'节假日'},
                    {value:310, name:'下雨'},
                    {value:234, name:'排队等待时间'},
                    {value:135, name:'客流量'},
                    {value:234, name:'地铁指数'},
                    {value:234, name:'公交指数'}
                ],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                itemStyle: {
                    normal: {
                        label:{
                            show: true,
                            position:'outside',
                            formatter: '{b}'
                        }
                    },
                    labelLine :{show:true}
                }
            }
        ]
    };
    courserate.setOption(option);

    /* =======*/
    var professionrate = echarts.init(document.getElementById('professionrate'));
    var total = {
        name: '=='
    };
    option = {
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            right: '0',
            y:'middle',
            textStyle:{
                color:"#fff"
            },
            data: ['公交车','长途车','小车'],
            formatter:function(name){
                var oa = option.series[0].data;
                var num = oa[0].value + oa[1].value + oa[2].value;
                for(var i = 0; i < option.series[0].data.length; i++){
                    if(name==oa[i].name){
                        return name +  ' '+oa[i].value;
                    }
                }
            }
        },
        series : [
            {
                name: 'FK',
                type: 'pie',
                radius : '60%',
                center: ['35%', '50%'],
                data:[
                    {value:335, name:'公交车'},
                    {value:310, name:'长途车'},
                    {value:234, name:'小车'}
                ],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                itemStyle: {
                    normal: {
                        label:{
                            show: true,
                            position:'outside',
                            formatter: '  {b}'
                        }
                    },
                    labelLine :{show:true}
                }
            }
        ]
    };
    professionrate.setOption(option);
 
    /* 比例变化*/
    var changedetail = echarts.init(document.getElementById('changedetail'));
    var total = {
        name: '=='
    };
    option = {
        tooltip: {
            trigger: 'axis',
            formatter: '{b}</br>{a}: {c}</br>{a1}: {c1}'
        },
        toolbox: {
            show:false,
            feature: {
                dataView: {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        legend: {
            data:['',''],
            show:false
        },
        grid:{
            top:'18%',
            right:'5%',
            bottom:'8%',
            left:'5%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: ['2021年','2022年','2023年','2024年','2025年'],
                splitLine:{
                    show:false,
                    lineStyle:{
                        color: '#3c4452'
                    }
                },
                axisTick: {
                    show: false
                },
                axisLabel:{
                    textStyle:{
                        color:"#fff"
                    },
                    lineStyle:{
                        color: '#519cff'
                    },
                    alignWithLabel: true,
                    interval:0
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: '小车(车次)',
                nameTextStyle:{
                    color:'#fff'
                },
                interval: 5,
                max:50,
                min: 0,
                splitLine:{
                    show:true,
                    lineStyle:{
                        color: '#23303f'
                    }
                },
                axisLine: {
                    show:false,
                    lineStyle: {
                        color: '#115372'
                    }
                },
                axisTick: {
                    show: false
                },
                axisLabel:{
                    textStyle:{
                        color:"#fff"
                    },
                    alignWithLabel: true,
                    interval:0

                }
            },
            {
                type: 'value',
                name: '大车(车次)',
                nameTextStyle:{
                    color:'#fff'
                },
                splitLine:{
                    show:true,
                    lineStyle:{
                        color: '#23303f'
                    }
                },
                axisLine: {
                    show:false,
                    lineStyle: {
                        color: '#115372'
                    }
                },
                axisTick: {
                    show: false
                },
                axisLabel:{
                    textStyle:{
                        color:"#fff"
                    },
                    alignWithLabel: true,
                    interval:0

                }
            }
        ],
        color:"yellow",
        series: [
            {
                name:'test1',
                type:'bar',
                data:[9, 14, 17, 25, 35],
                boundaryGap: '45%',
                barWidth:'40%',

                itemStyle: {
                    normal: {
                        color: function(params) {
                            var colorList = [
                                '#6bc0fb','#7fec9d','#fedd8b','#ffa597','#84e4dd'
                            ];
                            return colorList[params.dataIndex]
                        },label: {
                            show: true,
                            position: 'top',
                            formatter: '{c}'
                        }
                    }
                }
            },

            {
                name:'test2',
                type:'line',
                yAxisIndex: 1,
                lineStyle: {
                    normal: {
                        color:'#c39705'
                    }
                },
                data:[11, 13, 18, 24, 28]
            }
        ]
    };
    changedetail.setOption(option);

    /* ===*/
    var juniorservice = echarts.init(document.getElementById('juniorservice'));
    // 设置图表的选项
    var option = {
        title: {
            // text: '站内卡口车辆计数（当日）',
            left: 'center',
            textStyle: {
                fontSize: 16,
                color: '#ffffff' // 设置标题字体颜色为白色
            }
        },
        legend: {
            data: ['公交车站车辆', '长途车站车辆', '停车场车辆'],
            top: '20px',
            textStyle: {
                color: '#ffffff' // 设置图例字体颜色为白色
            }
        },
        grid: {
                left: '1%',
                right: '1%',
                bottom: '1%',
                containLabel: true
        },
        xAxis: {
            type: 'category',
            data: ['0点', '1点', '2点', '3点', '4点', '5点', '6点', '7点', '8点', '9点', '10点', '11点', '12点', '13点', '14点', '15点', '16点', '17点', '18点', '19点', '20点', '21点', '22点', '23点'],
            axisLine: {
                lineStyle: {
                    color: '#ffffff' // 设置X轴线条颜色为白色
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '车辆计数(辆)',
            min: 0,
            axisLine: {
                lineStyle: {
                    color: '#ffffff' // 设置Y轴线条颜色为白色
                }
            },
            axisLabel: {
                color: '#ffffff' // 设置Y轴标签字体颜色为白色
            }
        },
        series: [
            {
                name: '公交车站车辆',
                type: 'bar',
                data: [120, 132, 101, 134, 90, 230, 210, 180, 190, 201, 154, 190, 330, 410, 320, 340, 360, 420, 370, 250, 280, 240, 220],
                barWidth: '30%',
                itemStyle: {
                    color: '#76EE00', // 设置柱状图颜色为亮绿色
                    borderRadius: [5, 5, 5, 5], // 设置柱子的圆角边框
                    borderColor: '#ffffff', // 设置边框颜色
                    borderWidth: 1 // 设置边框宽度
                }
            },
            {
                name: '长途车站车辆',
                type: 'bar',
                data: [220, 182, 191, 234, 290, 330, 310, 320, 302, 301, 334, 390, 330, 320, 312, 334, 301, 421, 438, 320, 310, 301, 334],
                barWidth: '30%',
                itemStyle: {
                    color: '#EE6666',
                    borderRadius: [5, 5, 5, 5], // 设置柱子的圆角边框
                    borderColor: '#ffffff', // 设置边框颜色
                    borderWidth: 1 // 设置边框宽度
                }
            },
            {
                name: '停车场车辆',
                type: 'line',
                data: [150, 232, 201, 154, 190, 330, 410, 320, 250, 270, 290, 340, 360, 370, 380, 390, 350, 420, 370, 300, 320, 310, 340],
                lineStyle: {
                    color: '#FFD700',
                    width: 3 // 设置折线图的线宽
                },
                symbol: 'circle',
                symbolSize: 8
            }
        ]
    };
    juniorservice.setOption(option);


    /* ===*/
    var edubalance = echarts.init(document.getElementById('edubalance'));
    var total = {
        name: '=='
    };
    var option = {
            title: {
                // text: '站内卡口车辆计数（月平均）',
                left: 'center',
                textStyle: {
                    fontSize: 16,
                    color: '#ffffff' // 设置标题字体颜色为白色
                }
            },
            legend: {
                data: ['公交车站车辆', '长途车站车辆', '停车场车辆'],
                top: '20px',
                textStyle: {
                    color: '#ffffff' // 设置图例字体颜色为白色
                }
            },
            grid: {
                left: '1%',
                right: '1%',
                bottom: '1%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
                axisLine: {
                    lineStyle: {
                        color: '#ffffff' // 设置X轴线条颜色为白色
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: '车辆计数(辆)',
                min: 0,
                axisLine: {
                    lineStyle: {
                        color: '#ffffff' // 设置Y轴线条颜色为白色
                    }
                },
                axisLabel: {
                    color: '#ffffff' // 设置Y轴标签字体颜色为白色
                }
            },
            series: [
                {
                    name: '公交车站车辆',
                    type: 'bar',
                    data: [120, 132, 101, 134, 90, 230, 210, 180, 190, 201, 154, 190],
                    barWidth: '30%',
                    itemStyle: {
                        color: '#76EE00', // 设置柱状图颜色为亮绿色
                        borderRadius: [5, 5, 5, 5], // 设置柱子的圆角边框
                        borderColor: '#ffffff', // 设置边框颜色
                        borderWidth: 1 // 设置边框宽度
                    }
                },
                {
                    name: '长途车站车辆',
                    type: 'bar',
                    data: [220, 182, 191, 234, 290, 330, 310, 320, 302, 301, 334, 390],
                    barWidth: '30%',
                    itemStyle: {
                        color: '#EE6666',
                        borderRadius: [5, 5, 5, 5], // 设置柱子的圆角边框
                        borderColor: '#ffffff', // 设置边框颜色
                        borderWidth: 1 // 设置边框宽度
                    }
                },
                {
                    name: '停车场车辆',
                    type: 'line',
                    data: [150, 232, 201, 154, 190, 330, 410, 320, 250, 270, 290, 340],
                    lineStyle: {
                        color: '#FFD700',
                        width: 3 // 设置折线图的线宽
                    },
                    symbol: 'circle',
                    symbolSize: 8
                }
            ]
        };
    edubalance.setOption(option);

})