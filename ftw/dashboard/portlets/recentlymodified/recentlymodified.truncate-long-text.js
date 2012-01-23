jq(function(){
    jq(window).bind("load", function() {
        jq('dl.portlet.portletRecent span.title a').smartTruncation();
        jq('dl.portlet.portletRecent dd.portletItem span.title').css('visibility','visible');
    });
});