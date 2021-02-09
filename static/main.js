var App = App || {};

App.tip = function (message, time) {
    time = time || 4000;
    let body = $('body');
    let obj = body.find('.toast');
    if (!obj.length) {
        obj = $('<div/>', {'class': 'toast'});
        body.append(obj);
    }
    obj.html(message);
    window.setTimeout(function () {
        obj.remove();
    }, time);
};

$(function () {
    $(document).on('click', '.ajax', function () {
        let $this = $(this);
        let tr = $this.parents('tr')

        $.ajax({
            type: 'GET',
            url: $this.data('href'),
            dataType: 'json',
            context: $this,
            beforeSend: function () {
                tr.addClass('tr-opacity')
            },
            error: function (jqXHR, statusText, error) {
                let data = JSON.parse(jqXHR.responseText)
                App.tip(data['msg'], 5000);
                tr.removeClass('tr-opacity')
            },
            success: function (result) {
                tr.remove();
            }
        });
    });

    $(document).on('click', '.submit', function () {
        let $this = $(this);
        let $form = $this.parents('form')
        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: $form.serialize(),
            dataType: 'json',
            context: $this,
            beforeSend: function () {
                $this.addClass('loading')
            },
            error: function (jqXHR, statusText, error) {
                let data = JSON.parse(jqXHR.responseText)
                App.tip(data['msg'], 5000);
                $this.removeClass('loading')
            },
            success: function (result) {
                window.location.reload();
            }
        });
    });

    $(document).on('click', '.ajax-modal', function () {
        let $this = $(this);
        let url = $this.data('href') || $this.attr('href');
        $.get(url, function (html) {
            let $container = $("body").find('.modal-container')
            if (!$container.length) {
                $('body').append(html)
            } else {
                $container.html($(html).find('.modal-container').html())
            }
            let $modal = $('.modal');
            $modal.addClass('active');
            $container = $modal.find('.modal-container')
            $container.find('.btn-clear').on('click', function () {
                $modal.removeClass('active');
                $container.html('')
            });
        });
        return false;
    });

    window.load_url = {};
    $(window).scroll(function () {
        let scrollTop = $(window).scrollTop();
        let scrollHeight = $(document).height();
        let windowHeight = $(window).height();
        if (scrollTop + windowHeight >= scrollHeight - 50) {
            let table = $('.table')
            let page_url = table.data('page')
            if (page_url && !window.load_url[page_url]) {
                window.load_url[page_url] = page_url
                $('.loading').removeClass('d-none')
                $.get(window.page_url, {'page': page_url}, function (data) {
                    table.find('tbody').append(data['html'])
                    table.data('page', data['page_url'])
                    $('.loading').addClass('d-none')
                });
            }
        }
    });
});