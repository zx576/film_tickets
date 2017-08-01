/**
 * Created by zx on 17-7-30.
 */

//全局变量

var g_data = {};
var cur_cinema_id = null;

// {#    添加热门城市#}
$(document).ready(function () {
    var city_alpha = city;
    var hot_city = city['HOT'];
    for (c of hot_city){
        var cty = '<li><a href="javascript:void(0);" class="city_">'+ c + '</a></li>';
// {#                var cty = '<li><a href="" class="city_">'+ c + '</a></li>';#}
        $('#hotarea').append(cty);
    }
});

// {#    点击选择城市， 显示下拉框#}
$(document).ready(function () {
    $(document).on('click', '#choose-city', function () {
        var allcity = city;
        var str_html = '';
        var alpha = generateBig_1();
        for (i of alpha){
            var str_div = '<div class="movie-choose-city">\
                    <p class="h4">{0}</p>\
                    <hr>\
                    <ul class="nav nav-pills" id="hotarea">'.format(i);
            var cities = city[i];
            for (c in cities){
                var li = '<li><a href="javascript:void(0);" class="city_">{0}</a></li>'.format(cities[c]);
                str_div = str_div + li
            }

            str_div = str_div + '</ul></div>';
            str_html = str_html + str_div
        }
// {#                alert('sss')#}
        $('#movie-choose-x').html(str_html)

    })

});

// {#    显示下拉框，点击选择新城市，更新路径导航#}
$(document).ready(function(){
    $(document).on('click','.city_',function() {
// {#            $('.city_').click(function () {#}

        var that = this;
        var cty = that.text;
        var districts = dct[cty];
// {#                console.log(districts);#}
        var dis_1 = districts[0];
        var new_bread = ' <li class="disabled">当前路径： </li>\
                  <li id="choose-city"><a href="javascript:void(0);">{0}</a><span class="caret"></span></li>\
                  <li id="choose-dis"><a href="javascript:void(0);">{1}</a><span class="caret"></span></li>\
                  <li id="choose-cine"><a href="javascript:void(0);" class="cine_">...</a><span class="caret"></span></li>'.format(cty, dis_1);
        $('#bread').html(new_bread);
        var str_ul = '<ul class="nav nav-pills" id="hotarea">';
        for (i in districts){
            var li = '<li><a href="javascript:void(0);" class="dis_">{0}</a></li>'.format(districts[i]);
            str_ul = str_ul + li
        }
        str_url = str_ul + '</ul>';
        $('#movie-choose-x').html(str_ul)

    })
});



// {#    点击面包屑上的 区县 下拉出其他区县#}
$(document).on('click', '#choose-dis', function () {
    var cty = $('#choose-city a').text();
// {#            console.log(cty)#}
    var districts = dct[cty];
        var str_ul = '<ul class="nav nav-pills" id="hotarea">';
        for (i in districts){
            var li = '<li><a href="javascript:void(0);" class="dis_">{0}</a></li>'.format(districts[i]);
            str_ul = str_ul + li
        }
        str_url = str_ul + '</ul>';
        $('#movie-choose-x').html(str_ul)

});



// {#       获取当前时间 #}
$(document).ready(function () {
    var today = new Date();
    var tomorrow = new Date(today.getTime() + (24 * 60 * 60 * 1000));
    var third = new Date(tomorrow.getTime() + (24 * 60 * 60 * 1000));
    var td = today.getFullYear() + '-' + ('0'+ (today.getMonth()+1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
    var tm = tomorrow.getFullYear() + '-' + ('0'+ (tomorrow.getMonth()+1)).slice(-2) + '-' + ('0'+tomorrow.getDate()).slice(-2);
    var th = third.getFullYear() + '-' + ('0'+(third.getMonth()+1)).slice(-2) + '-' + ('0'+third.getDate()).slice(-2);
    $('#choose-date').append(
        '<li class="active date_" id="{0}"><a href="javascript:void(0);">今天 {0}</a></li>\
                        <li id="{1}" class="date_"><a href="javascript:void(0);">明天 {1}</a></li>\
                        <li id="{2}" class="date_"><a href="javascript:void(0);">后天 {2}</a></li>'.format(td, tm, th)
    )
});

// {#    生成26个大写字母#}
function generateBig_1(){
var str = [];
for(var i=65;i<91;i++){
    str.push(String.fromCharCode(i));
}
return str;
}

// {#    下拉电影院列表#}
$(document).on('click', '#choose-cine', function () {
    var dis =  $('#choose-dis a').text();
    console.log(dis);
    console.log(g_data);
    data = g_data[dis];
// {#        console.log(dis);#}
    $('#movie-choose-x').html(data);
});

