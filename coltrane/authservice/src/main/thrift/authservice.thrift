# authservice.thrift
namespace java io.coltrane.auth.thrift

service AuthService {
   bool isHaveAccessToRepo(1:string userName, 2:string appDomain)
}
