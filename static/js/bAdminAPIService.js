'use strict';

var bAdminAPIService = angular.module('bAdminAPIService', ['authService']);

bAdminAPIService.factory('bAdminAPI', ['$log', '$http', 'gatekeeper', function($log, $http, gatekeeper) {
    var bAdminAPIFactory = {};
    var baseUrl = "http://localhost:5000/";

    bAdminAPIFactory.getUsers = function() {
        return $http.get(baseUrl+"brugere", {
            params: {
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            }
        });
    }

    bAdminAPIFactory.getUser = function(id) {
        return $http.get(baseUrl+"brugere/" + id, {
            params: {
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            }
        });
    }

    bAdminAPIFactory.getClubs = function() {
        return $http.get(baseUrl+"klubber", {
            params: {
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            }
        });        
    }
    
    bAdminAPIFactory.applyForMembership = function(clubObj) {
        var mreqs = clubObj.membershipRequests;
        mreqs.push(gatekeeper.userId);

        $log.debug("PUT club with membershipRequests: ", mreqs, " (original was: ", clubObj.membershipRequests, " )");

        return $http.put(baseUrl+"klubber/"+clubObj.id, 
            {
                "membershipRequests": mreqs,
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            });        
    }

    return bAdminAPIFactory;
}]);