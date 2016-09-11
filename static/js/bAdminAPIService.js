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

    bAdminAPIFactory.getUserPractices = function(id) {
        return $http.get(baseUrl+"brugere/" + id + "/traeningspas", {
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
    
    bAdminAPIFactory.getClub = function(id) {
        return $http.get(baseUrl+"klubber/" + id, {
            params: {
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            }
        });        
    }

    bAdminAPIFactory.applyForMembership = function(clubObj) {
        var mreqs = clubObj.membershipRequests.slice();
        mreqs.push(gatekeeper.userId);

        $log.debug("PUT club with membershipRequests: ", mreqs, " (original was: ", clubObj.membershipRequests, " )");

        return $http.put(baseUrl+"klubber/"+clubObj.id, 
            {
                "membershipRequests": mreqs,
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            });        
    }

    bAdminAPIFactory.confirmPractice = function(practiceObj) {
        // Move user from invited list to confirmed list
        var confirmed = practiceObj.confirmed;
        var rejected = practiceObj.rejected;
        var invited = practiceObj.invited;
        // Since currentUserPracties is invited+confirmed+rejected the user will
        // be in either invited (no selection yet) or rejected (rejected pressed 
        // at some earlier point). 
        var idx = invited.indexOf(parseInt(gatekeeper.userId));
        if (idx > -1) {
            confirmed.push(invited[idx]);
            invited.splice(idx, 1);
        } else {
            idx = rejected.indexOf(parseInt(gatekeeper.userId));
            confirmed.push(rejected[idx]);   
            rejected.splice(idx, 1);
        }
        
        // Send PUT request
        return $http.put(baseUrl+"traeningspas/"+practiceObj.id,
            {
                // If we don't send properties they will default to the existing
                // thus we only send updates.
                "confirmed": confirmed,
                "rejected": rejected,
                "invited": invited,
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            });
    }

    bAdminAPIFactory.rejectPractice = function(practiceObj) {
        // Move user from rejected list to rejected list
        var confirmed = practiceObj.confirmed;
        var rejected = practiceObj.rejected;
        var invited = practiceObj.invited;
        // Since currentUserPracties is invited+confirmed+rejected the user will
        // be in either invited (no selection yet) or confirmed (confirmed pressed 
        // at some earlier point). 
        var idx = invited.indexOf(parseInt(gatekeeper.userId));
        if (idx > -1) {
            rejected.push(invited[idx]);
            invited.splice(idx, 1);
        } else {
            idx = confirmed.indexOf(parseInt(gatekeeper.userId));
            rejected.push(confirmed[idx]);   
            confirmed.splice(idx, 1);
        }

        // Send PUT request
        return $http.put(baseUrl+"traeningspas/"+practiceObj.id,
            {
                // If we don't send properties they will default to the existing
                // thus we only send updates.
                "confirmed": confirmed,
                "rejected": rejected,
                "invited": invited,
                "userID": gatekeeper.userId,
                "userAccessToken": gatekeeper.userAccessToken
            });
    }    

    return bAdminAPIFactory;
}]);