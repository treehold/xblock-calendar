function CalendarBlock(runtime, element) {

        var handler_url = runtime.handler_url('grant_access');
        var endpoint_url = runtime.handler_url('endpoint');

        String.prototype.format = function() {
            var formatted = this;
            for (var i = 0; i < arguments.length; i++) {
                var regexp = new RegExp('\\{'+i+'\\}', 'gi');
                formatted = formatted.replace(regexp, arguments[i]);
            }
            return formatted;
        };

        $(document).ready(function()
        {
            $('img#success').hide();
        });

        $('button#cal-btn').click(function() {
            var calendarId = $('#calendarId').val();
            $('#calendarId').val("");
            $.ajax({
            type: "POST",
            url: endpoint_url,
            data: JSON.stringify({email: calendarId}),
            success: $('img#success').show()
            });
        });

        $('#calendarId').keypress(function(e) {
            if(e.which == 13) {
                $.ajax({
                type: "POST",
                url: endpoint_url,
                data: JSON.stringify({email: calendarId}),
                success: $('img#success').show()
                });
            }
        });

        $("a#synchronize").click(function() {
            var win = window.open('https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.readonly&response_type=code&client_id=596157636159-svpcup864oijtk6s4jd538sqs9156d6i.apps.googleusercontent.com&approval_prompt=force&access_type=offline&redirect_uri=http%3A%2F%2Flocalhost:8002{0}'.format(handler_url));
            setTimeout(function() {
            win.close();
            }, 6000);
    });
}