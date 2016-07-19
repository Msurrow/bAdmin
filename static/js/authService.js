'use strict';

var myAuthService = angular.module('authService', []);

myAuthService.factory('gatekeeper', ['$log', function($log) {
    var loggedIn = false
    var userId = -1
    var userName = ''

    var doLogin = function doLogin(uid, name) {
        $log.debug("gatekeeper setting user: "+uid+" , "+name);
        this.userId = uid;
        this.userName = name;
        this.loggedIn = true;
    }

    var doLogout = function doLogout() {
        $log.debug("gatekeeper unsetting user")
        this.userId = -1;
        this.userName = '';
        this.loggedIn = false;
    }

    return {
        loggedIn: loggedIn,
        userId: userId,
        userName: userName,
        doLogin: doLogin,
        doLogout: doLogout
    };
}]);