# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 11:37:39 2014

@author: sm1fg

    Construct the magnetic network and generate the adjustments to the
    non-magnetic atmosphere for mhs equilibrium.

"""
import numpy as np
import astropy.units as u

#============================================================================
# locate flux tubes and footpoint strength
#============================================================================
def get_flux_tubes(
                   model_pars,
                   coords,
                   option_pars
                  ):
    """ Obtain an array of x,y coordinates and corresponding vertical
    component value for the photospheric magnetic field  """

    xi, yi, Si = [0.]*u.Mm,  [0.]*u.Mm,  [0.1]*u.T  # x,y,Bz(r=0,z=0)

    # parameters for matching Mumford,Fedun,Erdelyi 2014
    if option_pars['l_mfe']:
        Si = [0.15]*u.T # 150mT SI units
    # parameters for matching Gent,Fedun,Mumford,Erdelyi 2014
    elif option_pars['l_single']:
        Si = [0.1]*u.T # 100mT SI units
    # parameters for matching Gent,Fedun,Erdelyi 2014 flux tube pair
    elif option_pars['l_tube_pair']:
        xi, yi, Si = (
                      u.Quantity([
                                [ 0.00],
                                [ 0.00],
                                [  .15],
                                [-0.15]
                               ], unit=u.Mm),
                      u.Quantity([
                                [  1.2],
                                [  1.2],
                                [-1.15],
                                [-1.25]
                               ], unit=u.Mm),
                      u.Quantity([
                                [  50e-3],
                                [  50e-3],
                                [  50e-3],
                                [  50e-3]
                               ], unit=u.T)
                     )# 50mT SI
    # parameters for matching Gent,Fedun,Erdelyi 2014 twisted flux tubes
    elif option_pars['l_multi_twist']:
        xi, yi, Si = (
                      u.Quantity([
                                [ 0.34],
                                [ 0.07],
                                [  .14],
                                [-0.31]
                               ], unit=u.Mm),
                      u.Quantity([
                                [ 0.20],
                                [ 0.33],
                                [ 0.04],
                                [-0.34]
                               ], unit=u.Mm),
                      u.Quantity([
                                [  50e-3],
                                [  50e-3],
                                [  50e-3],
                                [  50e-3]
                               ], unit=u.T)
                     )# 50mT SI
    elif option_pars['l_multi_netwk']:
        xi, yi, Si = (
            u.Quantity(np.random.uniform(-0.5, 0.5, model_pars['nftubes']),
            unit=u.Mm),
            u.Quantity(np.random.uniform(-0.5, 0.5, model_pars['nftubes']),
            unit=u.Mm),
            u.Quantity(np.ones(model_pars['nftubes'])*0.33,
            unit=u.T)
            )
        x1 = [-1.75, -0.75, 1.25,  1.00, -0.75]
        y1 = [-1.00,  0.50, 0.50, -1.50,  1.70]
        xi[  : 3] = xi[  : 3] + x1[0] * u.Mm
        xi[3 : 6] = xi[ 3: 6] + x1[1] * u.Mm
        xi[6 : 9] = xi[ 6: 9] + x1[2] * u.Mm
        xi[9 :12] = xi[ 9:12] + x1[3] * u.Mm
        xi[12:15] = xi[12:15] + x1[4] * u.Mm
        yi[  : 3] = yi[  : 3] + y1[0] * u.Mm
        yi[3 : 6] = yi[ 3: 6] + y1[1] * u.Mm
        yi[6 : 9] = yi[ 6: 9] + y1[2] * u.Mm
        yi[9 :12] = yi[ 9:12] + y1[3] * u.Mm
        yi[12:15] = yi[12:15] + y1[4] * u.Mm
    elif option_pars['l_multi_lanes']:
        xi, yi, Si = (
            u.Quantity(np.random.uniform(-0.3, 0.3, model_pars['nftubes']),
            unit=u.Mm),
            u.Quantity(np.random.uniform(-0.3, 0.3, model_pars['nftubes']),
            unit=u.Mm),
            u.Quantity(np.ones(model_pars['nftubes'])*0.5,
            unit=u.T)
            )
        xi[  : 3] = xi[  : 3] - 1.875 * u.Mm
        xi[3 : 6] = xi[ 3: 6] - 1.125 * u.Mm
        xi[6 : 9] = xi[ 6: 9] - 0.375 * u.Mm
        xi[9 :12] = xi[ 9:12] + 0.375 * u.Mm
        xi[12:15] = xi[12:15] + 1.125 * u.Mm
        xi[15:18] = xi[15:18] + 1.875 * u.Mm
    else:
        raise ValueError("in get_flux_tubes axial parameters need to be defined")

    return xi, yi, Si

#============================================================================
# Magnetic Field Construction (See. Fedun et.al 2011)
#============================================================================
def construct_magnetic_field(
                             x, y, z,
                             x0, y0, S,
                             model_pars,
                             option_pars,
                             physical_constants,
                             scales):
    """ Construct self similar magnetic field configuration
    Note if model_pars['B_corona'] = 0 then paper3 results otherwise paper 2
    """
    #Extract commonly used scales:
    z1 = model_pars['photo_scale']
    z2 = model_pars['chrom_scale']
    z3 = model_pars['corona_scale']
    f0 = model_pars['radial_scale']
    mu0 = physical_constants['mu0']
    g0  = physical_constants['gravity']
    #scale Bf1, Bf2 to sum to 1
    Bf1 = model_pars['phratio']
    Bf2 = model_pars['chratio']
    Bf3 = model_pars['coratio']
    Bbz = (model_pars['B_corona'])
    #define exponentials and derivatives, basis functions
    if option_pars['l_B0_expz']:
        B1z = Bf1 * np.exp(-z**2/z1**2)
        B2z = Bf2 * np.exp(-z/z2)
        B3z = Bf3 * np.exp(-z/z3)
        B0z = B1z + B2z + B3z
        B10dz= -2*z*B1z/z1**2                    - B2z/z2    - B3z/z3
        B20dz= -2*  B1z/z1**2 + 4*z**2*B1z/z1**4 + B2z/z2**2 + B3z/z3**2
        B30dz= 12*z*B1z/z1**4 - 8*z**3*B1z/z1**6 - B2z/z2**3 - B3z/z3**3
    elif option_pars['l_B0_rootz']:
        B0z = Bf2 * z2**(0.125) / (z + z2)**(0.125)
        B10dz = -0.125 * B0z / (z + z2)
        B20dz = 9./64. * B0z / (z + z2)**2
        B30dz = -153./512 * B0z / (z + z2)**3
    elif option_pars['l_B0_quadz']:
        B1z = Bf1 * z1**2 / (z**2 + z1**2)
        B2z = Bf2 * z2 /(z + z2)
        B3z = Bf3 * np.exp(-z/z3)#       B3z = Bf3 * z3 /(z + z3)
        B0z = B1z + B2z + B3z
        B10dz=- 2 * z *B1z**2/z1**2                    -  B2z**2/z2    -  B3z/z3
        B20dz=  8*z**2*B1z**3/z1**4 - 2*  B1z**2/z1**2 +2*B2z**3/z2**2 +2*B3z/z3**2
        B30dz=-48*z**3*B1z**4/z1**6 +24*z*B1z**3/z1**4 -6*B2z**4/z2**3 -6*B3z/z3**3
    else:
        raise ValueError("in mhs_model.flux_tubes.construct_magnetic_field \
                  option_pars all False for axial strength Z dependence")

    rr= np.sqrt((x-x0)**2 + (y-y0)**2)
    #self similarity functions
    fxyz= -0.5*rr**2 * B0z**2
    G0 = np.exp(fxyz/f0**2)
    #Define Field
    B0z2 = B0z*B0z
    Bx = -S * (x-x0) * (B10dz * B0z * G0)
    By = -S * (y-y0) * (B10dz * B0z * G0)
    Bz =  S * B0z2 * G0 + Bbz
    f02 = f0*f0
    G02 = G0*G0
    B0z3 = B0z2*B0z
    B0z4 = B0z3*B0z
    B10dz2 = B10dz**2
    #Define derivatives of Bx
    dxBx = - S * (B10dz * B0z * G0) + 2 * S * (x-x0)**2 * B10dz * B0z3 * G0/f02
    dyBx =   2 * S * (x-x0) * (y-y0) * B10dz * B0z3 * G0/f02
    dzBx = - 2 * S * (x-x0) * (B0z*B20dz + (1. + 2.*fxyz/f02)*B10dz2)*G0
    #Define derivatives By
    dyBy = - S * (B10dz * B0z * G0) \
           + 2 * S * (y-y0)**2       * B10dz * B0z3 * G0/f02
    dxBy =   2 * S * (x-x0) * (y-y0) * B10dz * B0z3 * G0/f02
    dzBy = - 2 * S * (y-y0) * (B0z*B20dz + (1. + 2.*fxyz/f02)*B10dz2)*G0
    #Magnetic Pressure and horizontal thermal pressure balance term
    pbbal= 0.5/mu0 * S**2 * G02 * (
           f02 * B0z * B20dz + 2 * fxyz * B10dz**2 - B0z4 ) + S * Bbz * G0 * (
           f02 * B20dz / B0z + (2 * fxyz - f02) * B10dz2 / B0z2)/mu0
    #density balancing B
#    import pdb; pdb.set_trace()
    rho_1 = \
            S**2 * G02 / mu0 /g0 * (
            (0.5*f02 + 2*fxyz) * B10dz*B20dz + 0.5*f02 * B0z*B30dz
             - 2. * B0z3*B10dz
            ) + 2 * S*Bbz * G0 * fxyz / f02 * B10dz/B0z / mu0 / g0 * (
            f02 * B20dz/B0z + (2 * fxyz - f02) * B10dz2/B0z2) + S*Bbz * G0 * (
            f02 * B30dz/B0z + (4*fxyz - 3*f02) * B20dz*B10dz*B0z2
              + 2 * f02 * B10dz**3/B0z3 ) / mu0 / g0
    B2x = (Bx * dxBx + By * dyBx + Bz * dzBx)/mu0
    B2y = (Bx * dxBy + By * dyBy + Bz * dzBy)/mu0

    print("pbbal.max() = ",pbbal.max().decompose())
    return pbbal, rho_1, Bx, By, Bz, B2x, B2y

#============================================================================
# Magnetic Field Construction (See. Fedun et.al 2011)
#============================================================================
def construct_pairwise_field(x, y, z,
                             xi, yi,
                             xj, yj,
                             Si, Sj,
                             model_pars,
                             option_pars,
                             physical_constants,
                             scales
                            ):
    """ Construct self similar magnetic field configuration """
    #Extract commonly used scales:
    z1 = model_pars['photo_scale']
    z2 = model_pars['chrom_scale']
    z3 = model_pars['corona_scale']
    f0 = model_pars['radial_scale']
    mu0 = physical_constants['mu0']
    g0  = physical_constants['gravity']
    #scale Bf1, Bf2 to sum to 1
    Bf1 = model_pars['phratio']
    Bf2 = model_pars['chratio']
    Bf3 = model_pars['coratio']
    Bbz = (model_pars['B_corona'])
    #define exponentials and derivatives, basis functions
    if option_pars['l_B0_expz']:
        B1z = Bf1 * np.exp(-z**2/z1**2)
        B2z = Bf2 * np.exp(-z/z2)
        B3z = Bf3 * np.exp(-z/z3)
        B0z = B1z + B2z + B3z
        B10dz= -2*z*B1z/z1**2                    - B2z/z2    - B3z/z3
        B20dz= -2*  B1z/z1**2 + 4*z**2*B1z/z1**4 + B2z/z2**2 + B3z/z3**2
        B30dz= 12*z*B1z/z1**4 - 8*z**3*B1z/z1**6 - B2z/z2**3 - B3z/z3**3
    else:
        #if option_pars['l_BO_quadz']:
        B1z = Bf1 * z1**2 / (z**2 + z1**2)
        B2z = Bf2 * z2 /(z + z2)
        B3z = Bf3 * np.exp(-z/z3)
#        B3z = Bf3 * z3 /(z + z3)
        B0z = B1z + B2z + B3z
        B10dz=- 2 * z *B1z**2/z1**2                    -  B2z**2/z2    -  B3z/z3
        B20dz=  8*z**2*B1z**3/z1**4 - 2*  B1z**2/z1**2 +2*B2z**3/z2**2 +2*B3z/z3**2
        B30dz=-48*z**3*B1z**4/z1**6 +24*z*B1z**3/z1**4 -6*B2z**4/z2**3 -6*B3z/z3**3
    B10dz2 = B10dz**2
    BB10dz = B10dz*B0z
    BB10dz2 = BB10dz**2
    BB20dz = B20dz*B0z
#    B30dz= -B1z/z1**3 - B2z/z2**3
    ri= np.sqrt((x-xi)**2 + (y-yi)**2)
    rj= np.sqrt((x-xj)**2 + (y-yj)**2)
    ri2 = ri**2
    rj2 = rj**2
    ri4 = ri2**2
    rj4 = rj2**2
    #self similarity functions
    fxyzi= -ri2 * B0z**2/2.
    fxyzj= -rj2 * B0z**2/2.
    f02 = f0*f0
    G0i = np.exp(fxyzi/f02)
    G0j = np.exp(fxyzj/f02)
    G0ij = G0i*G0j
#Define Field
    Bxi = -Si * (x-xi) * (B10dz * B0z * G0i)
    Byi = -Si * (y-yi) * (B10dz * B0z * G0i)
    Bzi =  Si * B0z**2 * G0i + Bbz
    Bxj = -Sj * (x-xj) * (B10dz * B0z * G0j)
    Byj = -Sj * (y-yj) * (B10dz * B0z * G0j)
    Bzj =  Sj * B0z**2 * G0j + Bbz

    B0z2 = B0z*B0z
    B0z3 = B0z2*B0z
    B0z4 = B0z3*B0z


        #Magnetic Pressure and horizontal thermal pressure balance term
    pbbal= (0.5 * Si*Sj*G0ij * (f02*(B10dz2 + B0z*B20dz) - B0z4)
           -0.5 * Bbz*B10dz2 * (Si*ri2*G0i + Sj*rj2*G0j)
           +      Bbz*B20dz/B0z*f02 * (Si*G0i + Sj*G0j)      )/mu0

        #density balancing B
    rho_1 = \
            2.*Si*Sj*G0ij*BB10dz*(
            + (fxyzi + fxyzj) * (B10dz2/B0z2 + B20dz/B0z)
            - ((fxyzi + fxyzj)/f02 + 2.) * B0z2
            + 0.5*f02 * (3.*B20dz/B0z + B30dz/B10dz)
            +((x-xi)*(x-xj) + (y-yi)*(y-yj)) * ((
            1. + (fxyzi + fxyzj)/f02) * B10dz2 + BB20dz - B0z4/f02)
            ) + Bbz * Si*G0i * (B30dz/B0z*f02 - ri2*B20dz*B10dz
              - 0.5*B10dz2*BB10dz*ri4/f02 + (ri2-f02/B0z2)*B20dz*B10dz
            ) + Bbz * Sj*G0j * (B30dz/B0z*f02 - rj2*B20dz*B10dz
              - 0.5*B10dz2*BB10dz*rj4/f02 + (rj2-f02/B0z2)*B20dz*B10dz
            )
    rho_1 /= (g0 * mu0)
    Fx   = - 2*Si*Sj/mu0 * G0ij*BB10dz2*B0z2 * (
               (x-xi) * fxyzi/f02
             + (x-xj) * fxyzj/f02
                                               )
    Fy   = - 2*Si*Sj/mu0 * G0ij*BB10dz2*B0z2 * (
               (y-yi) * fxyzi/f02
             + (y-yj) * fxyzj/f02
                                               )
    #Define derivatives of Bx
    dxiBx = - Si * (BB10dz * G0i) \
            + 2 * Si * (x-xi)**2       * B10dz * B0z3 * G0i/f02
    dyiBx =   2 * Si * (x-xi) * (y-yi) * B10dz * B0z3 * G0i/f02
    dziBx = -     Si * (x-xi) * (B0z*B20dz + (1. + 2.*fxyzi/f02)*B10dz2)*G0i
    dxjBx = - Sj * (BB10dz * G0j) \
            + 2 * Sj * (x-xj)**2       * B10dz * B0z3 * G0j/f02
    dyjBx =   2 * Sj * (x-xj) * (y-yj) * B10dz * B0z3 * G0j/f02
    dzjBx = -     Sj * (x-xj) * (B0z*B20dz + (1. + 2.*fxyzj/f02)*B10dz2)*G0j
    #Define derivatives By
    dxiBy = - Si * (BB10dz * G0i) \
            + 2 * Si * (y-yi)**2       * B10dz * B0z3 * G0i/f02
    dyiBy =   2 * Si * (x-xi) * (y-yi) * B10dz * B0z3 * G0i/f02
    dziBy = -     Si * (y-yi) * (B0z*B20dz + (1. + 2.*fxyzi/f02)*B10dz2)*G0i
    dxjBy = - Sj * (BB10dz * G0j) \
            + 2 * Sj * (y-yj)**2       * B10dz * B0z3 * G0j/f02
    dyjBy =   2 * Sj * (x-xj) * (y-yj) * B10dz * B0z3 * G0j/f02
    dzjBy = -     Sj * (y-yj) * (B0z*B20dz + (1. + 2.*fxyzj/f02)*B10dz2)*G0j
    B2x = (Bxi * dxjBx + Byi * dyjBx + Bzi * dzjBx
         + Bxj * dxiBx + Byj * dyiBx + Bzj * dziBx)/mu0
    B2y = (Bxi * dxjBy + Byi * dyjBy + Bzi * dzjBy
         + Bxj * dxiBy + Byj * dyiBy + Bzj * dziBy)/mu0

    print"pbbal.max() = ",pbbal.max()
    return pbbal, rho_1, Fx, Fy, B2x, B2y
