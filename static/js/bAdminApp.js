'use strict';   // See note about 'use strict'; below

var myApp = angular.module('bAdminApp', [
    'ngRoute',
    'ui.bootstrap',
    'authService',
    'bAdminAPIService'
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
            when('/findClub', {
                templateUrl: '/static/partials/findClub.html',
            }).
            when('/createClub', {
                templateUrl: '/static/partials/createClub.html',
            }).
            when('/adminClub/:clubId', {
                templateUrl: '/static/partials/adminClub.html',
            }).
            otherwise({
                redirectTo: '/'
            });
    }]);

myApp.run(['$rootScope', '$window', '$log', 'gatekeeper', '$location', function($rootScope, window, $log, gatekeeper, $location) {
    // This is called with the results from from FB.getLoginStatus().
    function statusChangeCallback(response) {
        $log.debug('OAuth login: Call to statusChangeCallback. ', response);

        // The response object is returned with a status field that lets the
        // app know the current login status of the person.
        // Full docs on the response object can be found in the documentation
        // for FB.getLoginStatus().
        if (response.status === 'connected') {
            // Logged into your app and Facebook.
            FB.api('/me', {fields: "id, name, email"}, function(response) {
                $log.debug('OAuth login: Successful login for: ' + response.name);
                
                gatekeeper.doLogin(response.id, response.name, response.email);
                $("fb-login-button").text("Log ud");                
                $location.path("/#/");
                $rootScope.$apply();
            });
        } else if (response.status === 'not_authorized') {
            // The person is logged into Facebook, but not your app.
            $log.debug('OAuth login: User logged into facebook, but app is not authorized.');
            
            gatekeeper.doLogout();
            $("fb-login-button").text("Log ind");
            $location.path("/login");
            $rootScope.$apply();
        } else {
            // The person is not logged into Facebook, so we're not sure if
            // they are logged into this app or not.
            $log.debug('OAuth login: User not logged into Facebook');

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
        $log.debug("OAuth login: fbAsyncInit() called.")
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
        //Re-render all Facebook buttons
        if(typeof(FB) != 'undefined') {FB.XFBML.parse();}
    });    
}]);

myApp.controller('indexController', ['$rootScope', '$scope', '$log', '$location', 'gatekeeper', 'bAdminAPI', function($rootScope, $scope, $log, $location, gatekeeper, bAdminAPI) {
    $scope.currentUserId; //id: <int>, not null
    $scope.currentUserName; //name: <string>, not null
    $scope.currentUserClubs = []; //clubs: <list:Club object>
    $scope.currentUserEmail; //email: <string>, valid email
    $scope.currentUserPhone; //phone: <int:8>, 8-digits valid DK phonenumber
    $scope.currentUserClubsAsCoachOrAdmin = []; //clubs where user is admin or coach: <list:int>, int must be existing club ID and club will exist in currentUserClubs
    $scope.currentUserPractices = []; //practices the user is invited for (and confirmed, rejected): <list: practices object>

    //Init the controller
    (function(){
        if(!gatekeeper.loggedIn) {
            $log.debug("User not logged in, redirecting to /login");
            $location.path("/login");
        } else {
            bAdminAPI.getUser(gatekeeper.userId).then(
                function(response) {
                    $scope.currentUserId = response.data.id;
                    $scope.currentUserName = response.data.name;
                    $scope.currentUserPhone = response.data.phone;
                    $scope.currentUserEmail = response.data.email;
                    
                    //Resolve all user clubs
                    angular.forEach(response.data.clubs, function(clubId) {
                        bAdminAPI.getClub(clubId).then(
                            function(response) {
                                $scope.currentUserClubs.push(response.data);

                                if (response.data.admins.indexOf($scope.currentUserId) > -1) {
                                    $scope.currentUserClubsAsCoachOrAdmin.push(response.data);
                                } else if (response.data.coaches.indexOf($scope.currentUserId) > -1) {
                                    //A person can be both admin and coach in the same club
                                    //and we do not want the same club added twice. Thus we only 
                                    //check if person is coach if he is not already admin.
                                    $scope.currentUserClubsAsCoachOrAdmin.push(response.data);
                                }
                            },
                            function(error) {
                                $log.debug("Error response from API call:");
                                $log.debug(error);
                            });                        
                    });

                    // Get currentUser practices
                    bAdminAPI.getUserPractices($scope.currentUserId).then(
                            function(response) {
                                $scope.currentUserPractices = response.data;
                            },
                            function(error) {
                                $log.debug("Error response from API call:");
                                $log.debug(error);
                            });

                    $rootScope.currentUserName = $scope.currentUserName;
                }, 
                function(error) {
                    // User did not exits. If we are logged in, try to create the user
                    // and redo request
                    if (gatekeeper.loggedIn) {
                        // Service gets all arguments from gatekeeper
                        bAdminAPI.saveNewUser().then(
                            function(response) {
                                // Reload index again
                                $location.path("#");
                            },
                            function(error) {
                                $log.debug("Error response from API call:");
                                $log.debug(error);
                            });
                    }
                }
            );
        }
    })();

    $scope.formatDate = function(date) {
        moment.locale("da");
        return moment.utc(date).format("dddd H[:]mm, D MMM Y");
    }

    var updatePractices = function() {
                            $log.debug("updating practices..");
                            bAdminAPI.getUserPractices($scope.currentUserId).then(
                                function(response) {
                                    $log.debug("practices updated:");
                                    $log.debug(response.data);
                                    $scope.currentUserPractices = response.data;
                                },
                                function(error) {
                                    $log.debug("Error response from API call:");
                                    $log.debug(error);
                                });  
                        } 

    $scope.confirmPractice = function(practice) {
        // Check if the user pressed the confirm button again, ignore if so
        if($scope.practiceSelectionIsConfirmed(practice)) {
            return;
        }

        bAdminAPI.confirmPractice(practice).then(
            function(response) {
                $log.debug("confirm practice", practice);
                updatePractices();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);                
            });
    };  

    $scope.rejectPractice = function(practice) {
        // Check if the user pressed the reject button again, ignore if so
        if($scope.practiceSelectionIsRejected(practice)) {
            return;
        }

        bAdminAPI.rejectPractice(practice).then(
            function(response) {
                updatePractices();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);                
            });;
    }

    $scope.practiceSelectionIsConfirmed = function(practice) {
        var idx = $scope.currentUserPractices.indexOf(practice);        
        return $scope.currentUserPractices[idx].confirmed.indexOf($scope.currentUserId) > -1;
    }

    $scope.practiceSelectionIsRejected = function(practice) {
        var idx = $scope.currentUserPractices.indexOf(practice);        
        return $scope.currentUserPractices[idx].rejected.indexOf($scope.currentUserId) > -1;
    }

    $scope.isCoachOrAdmin = function(club) {
        if ($scope.currentUserClubsAsCoachOrAdmin.indexOf(club) > -1) {
            return true;
        } else {
            return false;
        }
    }
}]);

myApp.controller('findClubController', ['$scope', '$log', '$location', 'gatekeeper', 'bAdminAPI', function($scope, $log, $location, gatekeeper, bAdminAPI) {
    $scope.listOfClubs;
    $scope.currentUser;
    $scope.searchText = "";

    var updateClubs = function() {
        bAdminAPI.getClubs().then(
            function(response) {
                $scope.listOfClubs = response.data;
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);
            }
        );    
    };

    var updateUser = function() {
        bAdminAPI.getUser(gatekeeper.userId).then(
            function(response) {
                $scope.currentUser = response.data;
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);
            });
    };

    //Init the controller
    (function(){    
        if(!gatekeeper.loggedIn) {
            $log.debug("User not logged in, redirecting to /login");
            $location.path("/login");
        } else {
            updateUser();
            updateClubs();
        }
    })();

    $scope.applyAsMember = function(club) {
        bAdminAPI.applyForMembership(club).then(
            function(response) {
                updateUser();
                updateClubs();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);                
            });
    }

    $scope.userAlreadyMember = function(club) {
        var result = false;

        angular.forEach($scope.currentUser.clubs, function(clubId) {
            if (clubId == club.id) {
                result = true;
            }
        });

        return result;        
    }

    $scope.membershipAlreadyRequested = function(club) {
        var result = false;

        angular.forEach(club.membershipRequests, function(memReqUserId) {
            if (memReqUserId == gatekeeper.userId) {
                result = true;
            }
        });

        return result;
    }
}]);

myApp.controller('aboutController', ['$log', 'gatekeeper', '$location', function($log, gatekeeper, $location) {
    //Init the controller   
    (function(){
        if(!gatekeeper.loggedIn) {
            $log.debug("User not logged in, redirecting to /login");
            $location.path("/login");
        }
    })();
}]);

myApp.controller('createClubController', ['$scope', '$log', 'gatekeeper', '$location', '$routeParams', 'bAdminAPI', function($scope, $log, gatekeeper, $location, $routeParams, bAdminAPI) {
    $scope.newClubName = "";

    //Init the controller   
    (function(){
        if(!gatekeeper.loggedIn) {
            $log.debug("User not logged in, redirecting to /login");
            $location.path("/login");
        }
    })();

    $scope.submitNewClub = function() {
        bAdminAPI.saveNewClub($scope.newClubName).then(
            function(response) {
                $location.path("#");
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error); 
            });
    }
}]);

myApp.controller('adminClubController', ['$scope', '$log', 'gatekeeper', '$location', '$routeParams', 'bAdminAPI', function($scope, $log, gatekeeper, $location, $routeParams, bAdminAPI) {
    $scope.currentClubId = -1;
    $scope.currentClub;
    $scope.showPractices = true;
    $scope.showPlayers = false;
    $scope.showEditClub = false;
    $scope.currentClubPractices = [];

    //New practice vars
    $scope.newPracticeName = "";
    $scope.newPracticeDate = "";
    $scope.newPracticeStartHour = "";
    $scope.newPracticeStartMinute = "";
    $scope.newPracticeDuration = "";
    $scope.newPracticeRepeats = "";
    $scope.newPracticeInvitedPlayers = [];

    //Membership adm vars
    $scope.currentClubMembers = [];
    $scope.currentClubMembershipRequestUsers = [];

    //Init the controller   
    (function(){
        if(!gatekeeper.loggedIn) {
            $log.debug("User not logged in, redirecting to /login");
            $location.path("/login");
        }

        //Load club        
        $scope.currentClubId = $routeParams.clubId;
        bAdminAPI.getClub($scope.currentClubId).then(
            function(response) {
                $scope.currentClub = response.data;
                updateClubPractices();
                updateMembershipRequestUsers();
                updateClubMemberships();
            }, 
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);    
            });
    })();

    var updateClubPractices = function() {
        //Load practices
        bAdminAPI.getClubPractices($scope.currentClubId).then(
            function(response) {
                $scope.currentClubPractices = response.data;
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);  
            });
    }

    var updateMembershipRequestUsers = function() {
        //Reset the list as user objects will be resolved async, and we 
        //need to ensure we get a fresh list (no dublicates or old objects)
        $scope.currentClubMembershipRequestUsers = [];
        angular.forEach($scope.currentClub.membershipRequests, function(userId) {
            bAdminAPI.getUser(userId).then(
                function(response) {
                    $scope.currentClubMembershipRequestUsers.push(response.data);
                },
                function(error) {
                    $log.debug("Error response from API call:");
                    $log.debug(error);  
                });
        });
    }

    var updateClubMemberships = function() {
        bAdminAPI.getClubMembers($scope.currentClubId).then(
            function(response) {
                $scope.currentClubMembers = response.data;
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);  
            });
    }

    $scope.showPracticesFn = function() { $scope.showPractices = true; $scope.showPlayers = false; $scope.showEditClub = false; }
    $scope.showPlayersFn = function() { $scope.showPractices = false; $scope.showPlayers = true; $scope.showEditClub = false; }
    $scope.showEditClubFn = function() { $scope.showPractices = false; $scope.showPlayers = false; $scope.showEditClub = true; }

    $scope.submitNewPractice = function() {
        bAdminAPI.saveNewPractice($scope.currentClubId, $scope.newPracticeName, $scope.newPracticeDate, $scope.newPracticeStartHour, $scope.newPracticeStartMinute, $scope.newPracticeDuration, $scope.newPracticeRepeats, $scope.newPracticeInvitedPlayers).then(
            function(response) {
                updateClubPractices();
            }, 
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error); 
            }
        );

        $scope.newPracticeName = "";
        $scope.newPracticeDate = "";
        $scope.newPracticeStartHour = "";
        $scope.newPracticeStartMinute = "";
        $scope.newPracticeDuration = "";
        $scope.newPracticeRepeats = "";
        $scope.newPracticeInvitedPlayers = [];

        $scope.form.$setPristine();
        $scope.form.$setUntouched();
    }

    $scope.deletePractice = function(practice) {
        bAdminAPI.deletePractice(practice.id).then(
            function(response) {
                updateClubPractices();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);                
            });
    }

    $scope.acceptMemebershipRequest = function(user) {
        bAdminAPI.acceptMemebershipRequest($scope.currentClub, user).then(
            function(response) {
                // Updated club object is returned from the server.
                // Use this to update the local club obj membership request list.
                $scope.currentClub = response.data;
                updateMembershipRequestUsers();
                updateClubMemberships();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);  
            });
    }

    $scope.rejectMemebershipRequest = function(user) {
        bAdminAPI.rejectMemebershipRequest($scope.currentClub, user).then(
            function(response) {
                // Updated club object is returned from the server.
                // Use this to update the local club obj membership request list.
                $scope.currentClub = response.data;
                updateMembershipRequestUsers();
                updateClubMemberships();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error);  
            });
    }

    $scope.removeMember = function(user) {
        bAdminAPI.removeMemberFromClub($scope.currentClub, user).then(
            function(response) {
                updateClubMemberships();
            },
            function(error) {
                $log.debug("Error response from API call:");
                $log.debug(error); 
            });
    }

    $scope.formatDate = function(date) {
        return moment(date).format("dddd H[:]mm, D MMM Y");
    }
}]);


