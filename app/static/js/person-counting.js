    //setup before functions
    var typingTimer;                //timer identifier
    var doneTypingInterval = 5000;  //time in ms, 5 second for example
    var $inputKeyword = $('#city');

    $inputKeyword.keyup(() => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => search($inputKeyword.val()), 1000);
    });

    $inputKeyword.keydown(() => {
        clearTimeout(typingTimer);
    });

    function search(keyword) {
        console.log('keyword: ' + keyword);
        if(keyword === null || keyword.match(/^ *$/) !== null){ return;}
        $.ajax({
              type: 'GET',
              url: 'https://wft-geo-db.p.rapidapi.com/v1/geo/cities?limit=8&namePrefix='+keyword+'&offset=1',
              headers: {
                "x-rapidapi-host": "wft-geo-db.p.rapidapi.com",
                "x-rapidapi-key": "6f75ba224bmsh71043318e965eb4p198a77jsn376e283da129"
              },
              success: function(response) {
                    console.log(response)
                    var cityArray = response;
                    var dataCity = [];
                    for (var i = 0; i < cityArray.data.length; i++) {
                          dataCity[i] = cityArray.data[i].city; //countryArray[i].flag or null
                    }
                    console.log(dataCity);

                    $inputKeyword.autocomplete({
//                          data: ["abc", "def", "ghi"],
                          source: dataCity,
                          limit: 8, // The max amount of results that can be shown at once. Default: Infinity.
                    });
              }
        });
    }