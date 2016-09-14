'use strict';

var myAuthService = angular.module('authService', []);

myAuthService.factory('gatekeeper', ['$log', function($log) {
    var loggedIn = false
    var userId = -1
    var userName = ''
    var userEmail = ''
    var userAccessToken = 'facebook-access-token#TODO'

    var doLogin = function doLogin(uid, name, email) {
        $log.debug("gatekeeper setting user: "+uid+" , "+name+" ("+email+")");
        this.userId = uid;
        this.userName = name;
        this.userEmail = email;
        this.loggedIn = true;
    }

    var doLogout = function doLogout() {
        $log.debug("gatekeeper unsetting user")
        this.userId = -1;
        this.userName = '';
        this.userEmail = '';
        this.loggedIn = false;
    }

    return {
        loggedIn: loggedIn,
        userId: userId,
        userName: userName,
        userEmail: userEmail,
        doLogin: doLogin,
        doLogout: doLogout,
        userAccessToken: userAccessToken
    };
}]);