function CalendarBlock(runtime, element) {

        var handler_url = runtime.handler_url('endpoint');


        String.prototype.format = function() {
            var formatted = this;
            for (var i = 0; i < arguments.length; i++) {
                var regexp = new RegExp('\\{'+i+'\\}', 'gi');
                formatted = formatted.replace(regexp, arguments[i]);
            }
            return formatted;
        };

        function update_calendar(response) {
           document.getElementById("today", element).innerHTML=response.Today;
            $("#date-row").find("th").html(function (j) {
                var day = '{0}'.format(response.Order[j]);
                return response.Dates[day];
            });
            $(".evnt-list").empty();
            $(".happenings").find("ul").html(function (j) {
                var day = '{0}'.format(response.Order[j]);
                var toAppend = "";
                $.each(response.Events[day], function(index, value) {
                    toAppend += "<li> {0} </li>".format(value);
                });
                return toAppend;
            });

        }

        $('#previous-week').click(function(eventObject) {
            $.ajax({
                type: "POST",
                url: handler_url,
                data: JSON.stringify({travel: "backward"}),
                success: update_calendar
                });
        });


        $('#next-week').click(function(eventObject) {
                $.ajax({
                type: "POST",
                url: handler_url,
                data: JSON.stringify({travel: "forward"}),
                success: update_calendar
                });
        });

}