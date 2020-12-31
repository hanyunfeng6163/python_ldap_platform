/*
韩云峰添加
用来适配这个框架左侧菜单栏不能折叠的问题

其实这个模板原有的样式已经做到了折叠
问题是：
    不能折叠其他的菜单
 */
jQuery(function ($) {

    $(".parent-menu a").click(function () {
        let child = $(".child-group");
        let aa = $("a");

        // 点击a标签后，把所有这个标签父标签前后的所有都折叠，把show属性删除
        $(this).parent().prevAll().children(child).removeClass("show");
        $(this).parent().nextAll().children(child).removeClass("show");

        // 由于原有模板的问题，点击菜单后会保留字体颜色，这样都点击一遍后所有的都变成了蓝色；加上下面一句，当click操作时不要改变文字颜色
        $(this).css('color', '#000')


    });
});