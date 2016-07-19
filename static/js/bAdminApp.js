'use strict';   // See note about 'use strict'; below

var myApp = angular.module('bAdminApp', [
    'ngRoute',
    'ui.bootstrap',
    'authService'
]);

myApp.config(['$routeProvider', '$logProvider',
    function($routeProvider, $logProvider) {
        $logProvider.debugEnabled(true);

        $routeProvider.
            when('/', {
                templateUrl: '/static/partials/index.html',
            }).
            when('/login', {
                templateUrl: '/static/partials/login.html',
            }).
            when('/about', {
                templateUrl: '/static/partials/about.html',
            }).
            otherwise({
                redirectTo: '/'
            });
    }]);

myApp.run(['$rootScope', '$window', '$log', 'gatekeeper', '$location', function($rootScope, window, $log, gatekeeper, $location) {
    // This is called with the results from from FB.getLoginStatus().
    function statusChangeCallback(response) {
        $log.debug('statusChangeCallback');
        $log.debug(response);
        // The response object is returned with a status field that lets the
        // app know the current login status of the person.
        // Full docs on the response object can be found in the documentation
        // for FB.getLoginStatus().
        if (response.status === 'connected') {
            // Logged into your app and Facebook.
            FB.api('/me', {fields: "id, name"}, function(response) {
                $log.debug('Successful login for: ' + response.name);
                gatekeeper.doLogin(response.id, response.name);
                $("fb-login-button").text("Log ud");                
                $location.path("/#/");
                $rootScope.$apply();
            });
        } else if (response.status === 'not_authorized') {
            // The person is logged into Facebook, but not your app.
            $log.debug('Not logged into app');
            gatekeeper.doLogout();
            $("fb-login-button").text("Log ind");
            $location.path("/login");
            $rootScope.$apply();
        } else {
            // The person is not logged into Facebook, so we're not sure if
            // they are logged into this app or not.
            $log.debug('Not logged into Facebook');
            gatekeeper.doLogout();
            $("fb-login-button").text("Log ind"); 
            $location.path("/login");
            $rootScope.$apply();
        }
    }

    // This function is called when someone finishes with the Login
    // Button.  See the onlogin handler attached to it in the sample
    // code below.
    function checkLoginState() {
        FB.getLoginStatus(function(response) {
            statusChangeCallback(response);
        });
    }

    window.fbAsyncInit = function() {
        $log.debug("fbAsyncInit RUN")
        FB.init({
            appId      : '525282354344891',
            cookie     : true,  // enable cookies to allow the server to access 
                // the session
            xfbml      : true,  // parse social plugins on this page
            version    : 'v2.5' // use graph api version 2.5
            });

            FB.Event.subscribe('auth.login', function(response) {
                checkLoginState();
            });

            FB.Event.subscribe('auth.logout', function(response) {
                checkLoginState();
            });

            // Now that we've initialized the JavaScript SDK, we call 
            // FB.getLoginStatus().  This function gets the state of the
            // person visiting this page and can return one of three states to
            // the callback you provide.  They can be:
            //
            // 1. Logged into your app ('connected')
            // 2. Logged into Facebook, but not your app ('not_authorized')
            // 3. Not logged into Facebook and can't tell if they are logged into
            //    your app or not.
            //
            // These three cases are handled in the callback function.

            FB.getLoginStatus(function(response) {
                statusChangeCallback(response);
            });
    };

    // Load the SDK asynchronously
    (function(d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s); js.id = id;
        js.src = "//connect.facebook.net/en_US/sdk.js";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
}]);

myApp.controller('ngviewController', ['$scope', '$log', function($scope, $log) {
    $scope.$on('$viewContentLoaded', function() {
        $log.debug("ON viewContentLoaded");
        //Re-render all Facebook buttons
        FB.XFBML.parse();
    });    
}]);

myApp.controller('indexController', ['$scope', '$log', 'gatekeeper', '$location', function($scope, $log, gatekeeper, $location) {
    (function(){
        $log.debug("indexController init");
        if(!gatekeeper.loggedIn) {
            $log.debug("user not logged in, redirecting to /login");
            $location.path("/login");
        }
    })();
    
    // create a message to display in our view
    $scope.message = 'All the top secret stuff';
}]);

myApp.controller('aboutController', ['$log', 'gatekeeper', '$location', function($log, gatekeeper, $location) {
        (function(){
        $log.debug("aboutController init");
        if(!gatekeeper.loggedIn) {
            $log.debug("user not logged in, redirecting to /login");
            $location.path("/login");
        }
    })();
}]);