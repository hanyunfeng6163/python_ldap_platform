function object_delete(urls, id) {
        layer.confirm('是否删除？',{
            btn: ['确认', '取消'],
            title: false,
            closeBtn: false,
        },function () {
            $.get(urls +'/delete/' + id + '/', function (data) {
                    if (data['status'] === 0) {
                        layer.msg('删除成功', {
                            icon: 1,
                            time: 1500,
                            end: function () {
                                window.location.reload();
                            }
                        });
                    } else {
                        layer.msg('删除失败', {icon: 2});
                    }
                });
        },function () {
            layer.msg('已取消', {icon: 0});
        });
}