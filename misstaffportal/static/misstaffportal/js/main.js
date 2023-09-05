(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });


    // Progress Bar
    $('.pg-bar').waypoint(function () {
        $('.progress .progress-bar').each(function () {
            $(this).css("width", $(this).attr("aria-valuenow") + '%');
        });
    }, {offset: '80%'});


    // Calender
    $('#calender').datetimepicker({
        inline: true,
        format: 'L'
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        items: 1,
        dots: true,
        loop: true,
        nav : false
    });

    // appointment_chart.js

    var ctx1 = $("#appointmentchar").get(0).getContext("2d");

    // Define the data for each month as an array of objects
    var dataPerMonth = [
        { month: "Jan", pen: $("#appointmentchar").data("jan-pen"), pr: $("#appointmentchar").data("jan-pr"), com: $("#appointmentchar").data("jan-com"), tf: $("#appointmentchar").data("jan-tf") },
        { month: "Feb", pen: $("#appointmentchar").data("feb-pen"), pr: $("#appointmentchar").data("feb-pr"), com: $("#appointmentchar").data("feb-com"), tf: $("#appointmentchar").data("feb-tf") },
        { month: "Mar", pen: $("#appointmentchar").data("mar-pen"), pr: $("#appointmentchar").data("mar-pr"), com: $("#appointmentchar").data("mar-com"), tf: $("#appointmentchar").data("mar-tf") },
        { month: "Apr", pen: $("#appointmentchar").data("apr-pen"), pr: $("#appointmentchar").data("apr-pr"), com: $("#appointmentchar").data("apr-com"), tf: $("#appointmentchar").data("apr-tf") },
        { month: "May", pen: $("#appointmentchar").data("may-pen"), pr: $("#appointmentchar").data("may-pr"), com: $("#appointmentchar").data("may-com"), tf: $("#appointmentchar").data("may-tf") },
        { month: "June", pen: $("#appointmentchar").data("june-pen"), pr: $("#appointmentchar").data("june-pr"), com: $("#appointmentchar").data("june-com"), tf: $("#appointmentchar").data("june-tf") },
        { month: "July", pen: $("#appointmentchar").data("july-pen"), pr: $("#appointmentchar").data("july-pr"), com: $("#appointmentchar").data("july-com"), tf: $("#appointmentchar").data("july-tf") },
        { month: "Aug", pen: $("#appointmentchar").data("aug-pen"), pr: $("#appointmentchar").data("aug-pr"), com: $("#appointmentchar").data("aug-com"), tf: $("#appointmentchar").data("aug-tf") },
        { month: "Sept", pen: $("#appointmentchar").data("sept-pen"), pr: $("#appointmentchar").data("sept-pr"), com: $("#appointmentchar").data("sept-com"), tf: $("#appointmentchar").data("sept-tf") },
        { month: "Oct", pen: $("#appointmentchar").data("oct-pen"), pr: $("#appointmentchar").data("oct-pr"), com: $("#appointmentchar").data("oct-com"), tf: $("#appointmentchar").data("oct-tf") },
        { month: "Nov", pen: $("#appointmentchar").data("nov-pen"), pr: $("#appointmentchar").data("nov-pr"), com: $("#appointmentchar").data("nov-com"), tf: $("#appointmentchar").data("nov-tf") },
        { month: "Dec", pen: $("#appointmentchar").data("dec-pen"), pr: $("#appointmentchar").data("dec-pr"), com: $("#appointmentchar").data("dec-com"), tf: $("#appointmentchar").data("dec-tf") }
        ];
        
        // Extract the data for each status
        var pendingData = dataPerMonth.map(function(monthData) {
        return monthData.pen;
        });
        var inProgressData = dataPerMonth.map(function(monthData) {
        return monthData.pr;
        });
        var completeData = dataPerMonth.map(function(monthData) {
        return monthData.com;
        });
        var toFollowUpData = dataPerMonth.map(function(monthData) {
        return monthData.tf;
        });
        
        var myChart1 = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: dataPerMonth.map(function(monthData) {
            return monthData.month;
            }),
            datasets: [
            {
                label: "Pending",
                data: pendingData,
                backgroundColor: "rgba(23, 162, 184, 1)" // Blue
            },
            {
                label: "In Progress",
                data: inProgressData,
                backgroundColor: "rgba(0, 191, 255, .5)" // Sky Blue
            },
            {
                label: "Complete",
                data: completeData,
                backgroundColor: "rgba(40, 167, 69, 1)" // Green
            },
            {
                label: "To Follow-Up",
                data: toFollowUpData,
                backgroundColor: "rgba(255, 193, 7, 1)" // Yellow
            }
            ]
        },
        options: {
            responsive: true
        }
    });
        
})(jQuery);

