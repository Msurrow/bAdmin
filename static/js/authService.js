'use strict';

var myAuthService = angular.module('authService', []);

myAuthService.factory('gatekeeper', function() {
    var loggedIn = false
    var userId = -1
    var userName = ''

    var doLogin = function doLogin(userName, userId) {
        console.log("gatekeeper setting user")
        userId = userId;
        userName = userName;
        loggedIn = true;
    }

    var doLogout = function doLogout() {
        console.log("gatekeeper unsetting user")
        userId = -1;
        userName = '';
        loggedIn = false;
    }

    return {
        loggedIn: loggedIn,
        userId: userId,
        userName: userName,
        doLogin: doLogin
    };
});