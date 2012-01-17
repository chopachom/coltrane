# authservice.thrift

namespace java io.coltrane.auth.thrift
namespace py   io.coltrane.auth.thrift

service AuthService {
    bool checkCredentials(1:string username, 2:string password);
    bool canAccessRepo(1:string username, 2:string repo);
}